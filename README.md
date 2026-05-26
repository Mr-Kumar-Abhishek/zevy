# Zevy Messenger

> **Privacy-first, offline-capable peer-to-peer messenger** with Zero-Knowledge Proofs and Fully Homomorphic Encryption, built in Python (Kivy) and Rust.

---

## Overview

Zevy Messenger is a cross-platform P2P messaging application that operates **without any central server**. It uses real cryptographic primitives — **Groth16 Zero-Knowledge Proofs** (via `arkworks`) for identity verification and **Boolean Fully Homomorphic Encryption** (via `tfhe-rs`) for private computation — transmitted over persistent TCP sockets between peers on the same local network.

### Key Features

- **No Central Server** — All communication is peer-to-peer over local Wi-Fi, Bluetooth, or mDNS/TCP fallback.
- **Zero-Knowledge Identity** — Peers prove their identity using Groth16 ZKPs on the BN254 elliptic curve without revealing private keys.
- **Homomorphic Encryption** — Boolean values are encrypted, sent to a peer, computed upon *while still encrypted*, and the result is returned — the computing peer never sees the plaintext.
- **Cross-Platform** — Runs on Windows, macOS, and Linux as a desktop app; packagable as an Android APK via `buildozer`.
- **Dark Mode UI** — Modern OLED-black interface with glassmorphism chat bubbles, rounded buttons, and smooth transitions built with Kivy.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Kivy UI Layer                     │
│  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  DiscoveryScreen  │  │       ChatScreen          │  │
│  │  - Peer scanning  │  │  - Send/receive messages  │  │
│  │  - ZKP key display│  │  - HE encrypt/decrypt     │  │
│  └────────┬─────────┘  └────────────┬──────────────┘  │
│           │                         │                 │
├───────────┼─────────────────────────┼─────────────────┤
│           ▼                         ▼                 │
│  ┌─────────────────────────────────────────────────┐  │
│  │             NetworkManager (Singleton)           │  │
│  │  Routes packets through the active provider     │  │
│  └──────┬──────────────┬──────────────┬────────────┘  │
│         │              │              │               │
│  ┌──────▼─────┐ ┌──────▼─────┐ ┌─────▼──────────┐    │
│  │   mDNS/TCP  │ │ Wi-Fi Direct│ │   Bluetooth    │    │
│  │  Fallback   │ │  (pyjnius)  │ │   (pyjnius)    │    │
│  │  Port 8888  │ │  Port 8889  │ │   Port 8890    │    │
│  └─────────────┘ └─────────────┘ └────────────────┘    │
│                                                       │
├───────────────────────────────────────────────────────┤
│                 Rust Crypto Engine (PyO3)              │
│  ┌─────────────────────┐  ┌─────────────────────────┐ │
│  │  arkworks (Groth16)  │  │    tfhe-rs (Boolean)     │ │
│  │  - generate_zkp_keys │  │  - HEClient.encrypt_bool │ │
│  │  - generate_proof    │  │  - HEServer.compute_and  │ │
│  │  - verify_proof      │  │  - HEClient.decrypt_bool │ │
│  └─────────────────────┘  └─────────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

---

## Project Structure

```
zevy/
├── main.py                  # Application entry point (Kivy App + async network thread)
├── buildozer.spec           # Android packaging configuration
├── pytest.ini               # Test configuration
├── .gitignore
│
├── crypto_rust/             # Rust native extension (compiled via maturin)
│   ├── Cargo.toml           # Rust dependencies (tfhe, arkworks, pyo3)
│   ├── Cargo.lock
│   └── src/
│       └── lib.rs           # ZKP (Groth16/BN254) + FHE (TFHE boolean) implementations
│
├── network/                 # Networking layer
│   ├── __init__.py
│   ├── manager.py           # Abstract NetworkManager singleton
│   ├── protocol.py          # JSON packet serialization (HANDSHAKE, CHAT_MESSAGE, HE_*)
│   ├── mdns_fallback.py     # Persistent TCP server with async message loops
│   ├── wifi_direct.py       # Android WifiP2pManager via pyjnius (desktop fallback)
│   └── bluetooth.py         # Android BluetoothAdapter via pyjnius (desktop fallback)
│
├── ui/                      # User interface
│   ├── __init__.py
│   ├── components.kv        # Kivy language layout (dark mode, glassmorphism)
│   └── screens.py           # DiscoveryScreen + ChatScreen logic
│
├── tests/                   # Test suite (pytest)
│   ├── test_crypto.py       # ZKP key generation, proof, verification; HE encrypt/decrypt
│   ├── test_network.py      # NetworkManager lifecycle tests
│   ├── test_mdns.py         # mDNS TCP server start/stop tests
│   └── test_protocol.py     # Packet serialization round-trip tests
│
└── docs/                    # Design documents
    ├── software_requirement_specification.md
    ├── software_design_document.md
    └── implementation_plan.md
```

---

## Prerequisites

| Tool         | Version   | Purpose                                    |
|--------------|-----------|--------------------------------------------|
| Python       | ≥ 3.10    | Application runtime                        |
| Rust + Cargo | ≥ 1.70    | Compile the `crypto_rust` native extension |
| maturin      | ≥ 1.0     | Build and install the Rust→Python bridge   |
| Kivy         | ≥ 2.3     | Cross-platform UI framework                |

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url> zevy
cd zevy
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install kivy zeroconf pytest pytest-asyncio
```

### 4. Build and install the Rust crypto engine

```bash
cd crypto_rust
pip install maturin
maturin develop --release
cd ..
```

This compiles the `arkworks` (Groth16 ZKP) and `tfhe-rs` (Boolean FHE) Rust code into a native Python module named `crypto_rust`.

### 5. Run the application

```bash
python main.py
```

---

## Usage

### Discovery Screen

When the app launches, you are presented with three connectivity options:

| Button        | Protocol                 | Port  | Description                                  |
|---------------|--------------------------|-------|----------------------------------------------|
| **Bluetooth** | Android BLE / TCP mock   | 8890  | Uses `BluetoothAdapter` on Android, TCP on desktop |
| **Wi-Fi**     | Android Wi-Fi Direct / TCP mock | 8889 | Uses `WifiP2pManager` on Android, TCP on desktop |
| **Local Node**| mDNS + TCP               | 8888  | Works on all platforms via `zeroconf`         |

Each button:
1. Starts the `NetworkManager` in the selected mode.
2. Generates **arkworks Groth16 Zero-Knowledge Proof keys** (BN254 curve).
3. Opens a persistent TCP socket and connects to a peer.
4. Displays the peer with a truncated ZKP public key fingerprint.

### Chat Screen

Click on a discovered peer to enter the chat. When you send a message:

1. The message text is serialized into a `CHAT_MESSAGE` JSON packet and transmitted over the TCP socket.
2. A boolean value is encrypted using `tfhe-rs` Fully Homomorphic Encryption (`HEClient.encrypt_bool`).
3. The encrypted ciphertext is sent as an `HE_COMPUTE_REQ` packet to the peer.
4. The peer performs a **blind boolean AND** computation on the ciphertext (`HEServer.compute_and`) — **without ever decrypting it**.
5. The result ciphertext is returned as an `HE_COMPUTE_RES` packet.
6. Your client decrypts the result (`HEClient.decrypt_bool`) and displays it in the UI.

---

## Cryptography

### Zero-Knowledge Proofs (Groth16)

Zevy uses the **Groth16** proving system on the **BN254** (alt-bn128) elliptic curve, implemented via the [`arkworks`](https://github.com/arkworks-rs) Rust ecosystem.

| Function              | Description                                                 |
|-----------------------|-------------------------------------------------------------|
| `generate_zkp_keys()` | Runs a trusted setup, returning `(proving_key, verifying_key)` as hex strings |
| `generate_proof(pk, a, b)` | Creates a zk-SNARK proof that `a × b = c` without revealing `a` or `b` |
| `verify_proof(vk, c, proof)` | Verifies the proof against the public input `c` |

### Fully Homomorphic Encryption (TFHE)

Zevy uses the **TFHE** boolean encryption scheme from [`tfhe-rs`](https://github.com/zama-ai/tfhe-rs) by Zama.

| Class / Method               | Description                                              |
|------------------------------|----------------------------------------------------------|
| `HEClient()`                 | Generates a client key pair for boolean FHE              |
| `HEClient.get_evaluation_key()` | Exports the server (evaluation) key as bytes          |
| `HEClient.encrypt_bool(val)` | Encrypts a boolean into a ciphertext blob                |
| `HEClient.decrypt_bool(ct)`  | Decrypts a ciphertext blob back to a boolean             |
| `HEServer(eval_key)`         | Initializes a server-side evaluator from the eval key    |
| `HEServer.compute_and(ct_a, ct_b)` | Computes homomorphic AND on two encrypted booleans |

---

## Network Protocol

All peer communication uses **newline-delimited JSON** over persistent TCP sockets.

### Packet Format

```json
{"type": "CHAT_MESSAGE", "payload": {"msg": "Hello!"}}
```

### Packet Types

| Type             | Direction | Payload                              |
|------------------|-----------|--------------------------------------|
| `HANDSHAKE`      | Both      | `{zkp_public_key: "hex..."}`         |
| `CHAT_MESSAGE`   | Both      | `{msg: "text"}`                      |
| `HE_COMPUTE_REQ` | A → B     | `{cipher: <bytes>}`                  |
| `HE_COMPUTE_RES` | B → A     | `{res: <bytes>}`                     |

---

## Testing

Run the full test suite:

```bash
pytest
```

### Test Coverage

| Test File           | What it tests                                              |
|---------------------|------------------------------------------------------------|
| `test_crypto.py`    | ZKP key generation, proof creation, proof verification; HE encrypt → compute → decrypt round-trip |
| `test_network.py`   | `NetworkManager` mode switching, start/stop lifecycle      |
| `test_mdns.py`      | TCP server binding, start/stop, connection handling         |
| `test_protocol.py`  | Packet serialization and deserialization round-trip         |

---

## Android Build

Zevy can be packaged as an Android APK using [buildozer](https://github.com/kivy/buildozer).

### Prerequisites (Linux / WSL)

```bash
sudo apt install -y python3-pip openjdk-17-jdk autoconf automake libtool
pip install buildozer cython
```

### Build

```bash
buildozer android debug
```

The resulting `.apk` will be in `bin/`.

### Android Permissions

The `buildozer.spec` requests the following permissions:

- `INTERNET` — TCP socket communication
- `BLUETOOTH`, `BLUETOOTH_ADMIN`, `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN` — Bluetooth RFCOMM
- `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION` — Required for Wi-Fi Direct and BLE scanning
- `ACCESS_WIFI_STATE`, `CHANGE_WIFI_STATE` — Wi-Fi Direct P2P
- `NEARBY_WIFI_DEVICES` — Android 13+ Wi-Fi Direct requirement

---

## Development Methodology

This project was developed using **Agile methodology with Test-Driven Development (TDD)**:

| Sprint | Focus                                    | Status |
|--------|------------------------------------------|--------|
| 1      | Rust crypto engine (arkworks + tfhe-rs)  | ✅     |
| 2      | Crypto integration tests                 | ✅     |
| 3      | Network abstraction layer                | ✅     |
| 4      | Kivy UI integration                      | ✅     |
| 5      | Production TCP networking + protocol     | ✅     |
| 6      | Native Android networking (pyjnius)      | ✅     |
| 7      | Android APK packaging                    | 🔲     |

---

## License

This project is currently unlicensed. Add a `LICENSE` file to specify terms.
