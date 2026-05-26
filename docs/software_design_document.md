# Software Design Document (SDD)
## Zevy — Secure P2P Messenger

### 1. Introduction

This document details the architectural design, system components, and data flows
for Zevy Messenger — a privacy-first, offline-capable peer-to-peer messaging
application with cryptographic identity verification and private computation.

### 2. System Architecture

#### 2.1 High-Level Architecture

Zevy follows a modular, multi-threaded architecture:

| Layer                    | Technology           | Responsibility                                     |
|--------------------------|----------------------|----------------------------------------------------|
| **Presentation (UI)**    | Kivy + KV Language   | Screens, navigation, dark-mode rendering           |
| **Network Abstraction**  | Python asyncio       | Routing packets through Wi-Fi Direct / BLE / TCP   |
| **Crypto Engine**        | Rust (PyO3 → Python) | Zero-Knowledge Proofs (Groth16) + Homomorphic Encryption (TFHE) |

A background `asyncio` event loop runs in a daemon thread (`main.network_loop`)
so that network I/O never blocks the Kivy UI thread.

#### 2.2 Component Design

##### A. Kivy Presentation Layer (`ui/`)

| Component         | File              | Purpose                                          |
|-------------------|-------------------|--------------------------------------------------|
| `DiscoveryScreen` | `screens.py`      | Peer scanning, ZKP key generation, mode selection |
| `ChatScreen`      | `screens.py`      | Message send/receive, HE challenge/response       |
| `ChatBubble`      | `screens.py`      | Glassmorphism-styled message bubble widget        |
| `PeerButton`      | `screens.py`      | Styled button for discovered peers                |
| Layout            | `components.kv`   | Kivy language markup (OLED-black dark mode)       |

##### B. Network Abstraction Layer (`network/`)

| Component              | File               | Purpose                                                    |
|------------------------|--------------------|------------------------------------------------------------|
| `NetworkManager`       | `manager.py`       | Singleton that routes all packets through the active provider |
| `NetworkMode`          | `manager.py`       | Enum: `WIFI_DIRECT`, `BLUETOOTH`, `LOCAL_MDNS_FALLBACK`    |
| `MDNSFallbackProvider` | `mdns_fallback.py` | Persistent TCP server with async reader loops               |
| `WiFiDirectProvider`   | `wifi_direct.py`   | Android `WifiP2pManager` via pyjnius (TCP fallback on desktop) |
| `BluetoothProvider`    | `bluetooth.py`     | Android `BluetoothAdapter` via pyjnius (TCP fallback on desktop) |
| `PacketType`           | `protocol.py`      | Constants and serializers for the JSON packet protocol      |

##### C. Rust Crypto Engine (`crypto_rust/`)

| Symbol               | Type      | Cryptographic Primitive                               |
|----------------------|-----------|-------------------------------------------------------|
| `generate_zkp_keys`  | Function  | Groth16 trusted setup on BN254 → `(pk_hex, vk_hex)`  |
| `generate_proof`     | Function  | zk-SNARK proof that `a × b = c` without revealing `a`, `b` |
| `verify_proof`       | Function  | Verifies a Groth16 proof against the public input     |
| `HEClient`           | Class     | Client-side TFHE boolean key generation, encrypt, decrypt |
| `HEServer`           | Class     | Server-side evaluation (blind `AND` on ciphertexts)   |

### 3. Data Flow & Protocols

#### 3.1 Peer Discovery & Connection

```
User clicks "Local Node"
  │
  ▼
NetworkManager.start(LOCAL_MDNS_FALLBACK)
  │
  ├─► MDNSFallbackProvider.start()  →  asyncio TCP server on port 8888
  │
  ▼
NetworkManager.connect_to_peer("127.0.0.1", 8888)
  │
  ├─► asyncio.open_connection()  →  persistent reader task spawned
  │
  ▼
Peer appears in DiscoveryScreen with ZKP public key fingerprint
```

#### 3.2 Secure Handshake (Zero-Knowledge Proof)

1. On app launch, `DiscoveryScreen.__init__` calls `crypto_rust.generate_zkp_keys()`
   which runs a **Groth16 trusted setup** on the BN254 curve.
2. The resulting proving key (`pk`) and verifying key (`vk`) are stored.
3. A truncated hex fingerprint of the public key is displayed next to each
   discovered peer to visually confirm identity.
4. (Future) A `HANDSHAKE` packet will exchange the full `vk` and a proof so
   each peer can call `crypto_rust.verify_proof()` before unlocking chat.

#### 3.3 Chat Message Flow

```
User types "Hello" and clicks Send
  │
  ├─► CHAT_MESSAGE packet  ──► TCP socket  ──► Peer displays message
  │
  ├─► HEClient.encrypt_bool(True)
  │     └─► HE_COMPUTE_REQ packet  ──► TCP socket  ──► Peer
  │                                                      │
  │                                   HEServer.compute_and(ct, ct)
  │                                                      │
  │     HE_COMPUTE_RES packet  ◄── TCP socket  ◄─────────┘
  │
  └─► HEClient.decrypt_bool(result)  →  displayed in UI
```

The peer **never** sees the plaintext boolean — computation happens entirely
on the encrypted ciphertext.

#### 3.4 Packet Protocol

All packets are **newline-delimited JSON** (`\n`-terminated):

```json
{"type": "CHAT_MESSAGE", "payload": {"msg": "Hello!"}}
{"type": "HE_COMPUTE_REQ", "payload": {"cipher": "<bytes>"}}
{"type": "HE_COMPUTE_RES", "payload": {"res": "<bytes>"}}
```

### 4. Threading Model

```
┌─────────────────────────┐     ┌─────────────────────────┐
│   Main Thread (Kivy)    │     │  Daemon Thread (asyncio) │
│                         │     │                          │
│  UI rendering           │     │  network_loop.run_forever│
│  Button callbacks       │────►│  TCP read/write tasks    │
│  Clock.schedule_once    │◄────│  on_message callbacks    │
│                         │     │                          │
└─────────────────────────┘     └─────────────────────────┘
```

- `asyncio.run_coroutine_threadsafe()` bridges Kivy → asyncio.
- `kivy.clock.Clock.schedule_once()` bridges asyncio → Kivy (thread-safe UI updates).

### 5. Platform Abstraction

| Platform  | Wi-Fi Direct           | Bluetooth              | mDNS/TCP           |
|-----------|------------------------|------------------------|---------------------|
| Android   | `WifiP2pManager` (JNI) | `BluetoothAdapter` (JNI) | `zeroconf` + TCP |
| Desktop   | TCP fallback (port 8889) | TCP fallback (port 8890) | `zeroconf` + TCP (port 8888) |

Desktop fallbacks use the **same** `MDNSFallbackProvider` on different ports,
ensuring that all cryptographic operations (ZKP, HE) execute identically
regardless of the transport layer.

### 6. Security Considerations

- **No Central Server**: All data stays on the local network. There is no
  cloud relay, no metadata logging, no phone-home.
- **Forward Secrecy**: ZKP keys are regenerated on every app launch.
- **Blind Computation**: The HE server never accesses plaintext. It operates
  exclusively on encrypted ciphertexts.
- **Transport Layer**: TCP sockets are currently unencrypted (plaintext JSON).
  A future sprint should add TLS or Noise Protocol for wire encryption.
