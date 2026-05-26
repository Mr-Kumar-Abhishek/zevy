# Software Requirement Specification (SRS)
## Zevy — Secure P2P Messenger

### 1. Introduction

#### 1.1 Purpose
This document defines the software requirements for Zevy Messenger, a
privacy-first, decentralized, peer-to-peer messaging application. Zevy
operates entirely offline over local-area connections and uses advanced
cryptographic primitives for identity verification and private computation.

#### 1.2 Scope
Zevy is a fully decentralized communication tool that bypasses centralized
servers, internet service providers, and cellular networks. It communicates
exclusively via direct device-to-device connections (Bluetooth, Wi-Fi Direct,
or mDNS/TCP on a shared local network). It uses:

- **Zero-Knowledge Proofs** (Groth16 on BN254) for identity authentication.
- **Fully Homomorphic Encryption** (TFHE boolean scheme) for blind computation
  on encrypted data.

Both cryptographic backends are implemented in **Rust** for performance and
correctness, exposed to Python via PyO3.

#### 1.3 Definitions

| Term   | Definition                                                           |
|--------|----------------------------------------------------------------------|
| ZKP    | Zero-Knowledge Proof — proving a statement is true without revealing why |
| FHE    | Fully Homomorphic Encryption — computing on ciphertexts without decrypting |
| P2P    | Peer-to-Peer — direct device-to-device without a server             |
| mDNS   | Multicast DNS — local network service discovery                      |
| TFHE   | Torus-based Fully Homomorphic Encryption                             |
| PyO3   | Rust-to-Python FFI bridge                                            |

---

### 2. Overall Description

#### 2.1 Product Features

| ID  | Feature                         | Description                                                                 |
|-----|---------------------------------|-----------------------------------------------------------------------------|
| F1  | Bluetooth P2P Networking        | Device-to-device communication via Android BluetoothAdapter (RFCOMM)        |
| F2  | Wi-Fi Direct P2P Networking     | Ad-hoc Wi-Fi connections via Android WifiP2pManager                         |
| F3  | mDNS/TCP Local Fallback         | Cross-platform TCP connections via zeroconf for desktop and router networks |
| F4  | Zero-Knowledge Authentication   | Groth16 zk-SNARK proofs for identity verification without revealing secrets |
| F5  | Homomorphic Encrypted Compute   | Boolean FHE (TFHE) for blind computation between peers                      |
| F6  | Decentralized Chat              | Text-based P2P messaging with no central server                             |
| F7  | Cross-Platform UI               | Kivy-based dark mode interface for desktop and mobile                       |
| F8  | Desktop Mock Fallback           | All transport modes fall back to TCP on desktop, preserving crypto behavior  |

#### 2.2 Operating Environment

| Platform  | Runtime                    | Transport                                          |
|-----------|----------------------------|----------------------------------------------------|
| Android   | Python-for-Android (p4a)   | Wi-Fi Direct, Bluetooth (native), TCP fallback     |
| Windows   | CPython 3.10+              | TCP fallback (mDNS) on all three modes             |
| macOS     | CPython 3.10+              | TCP fallback (mDNS) on all three modes             |
| Linux     | CPython 3.10+              | TCP fallback (mDNS) on all three modes             |

#### 2.3 Technology Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| UI Framework   | Kivy 2.3 + KV Language                          |
| Crypto Backend | Rust — `arkworks` (Groth16/BN254) + `tfhe-rs`   |
| Rust→Python    | PyO3 + maturin                                   |
| Networking     | Python asyncio + TCP sockets + zeroconf          |
| Android Bridge | pyjnius (Python → JNI → Android SDK)             |
| Packaging      | buildozer (Android APK)                          |
| Testing        | pytest + pytest-asyncio                          |

#### 2.4 User Classes

- **Privacy Advocates:** Users requiring cryptographic guarantees against surveillance.
- **Off-Grid Users:** Users in areas without internet infrastructure who need local communication.
- **Developers:** Contributors interested in privacy-preserving P2P protocols.

---

### 3. Specific Requirements

#### 3.1 Functional Requirements

| ID   | Requirement                                                                                  | Status |
|------|----------------------------------------------------------------------------------------------|--------|
| FR1  | The app shall discover nearby peers via Bluetooth, Wi-Fi Direct, or mDNS/TCP.                | ✅      |
| FR2  | The app shall generate Groth16 ZKP keys (BN254 curve) on startup for identity verification.  | ✅      |
| FR3  | The app shall create and verify zk-SNARK proofs for peer authentication.                     | ✅      |
| FR4  | The app shall encrypt boolean values using TFHE and send ciphertexts to peers.               | ✅      |
| FR5  | The peer shall perform blind boolean AND computation on received ciphertexts.                | ✅      |
| FR6  | The app shall decrypt FHE results received from peers and display them in the UI.            | ✅      |
| FR7  | The app shall send and receive text messages over persistent TCP sockets.                    | ✅      |
| FR8  | All network modes shall fall back to TCP on desktop, preserving full crypto behavior.        | ✅      |
| FR9  | The app shall be packageable as an Android APK via buildozer.                                | 🔲      |

#### 3.2 Non-Functional Requirements

| ID    | Requirement                                                                                    | Status |
|-------|------------------------------------------------------------------------------------------------|--------|
| NFR1  | Cryptographic operations must run in a background thread to prevent UI freezing.               | ✅      |
| NFR2  | ZKP key generation shall complete in < 10 seconds on desktop hardware.                         | ✅      |
| NFR3  | The UI shall use a modern dark-mode aesthetic with OLED-black backgrounds.                     | ✅      |
| NFR4  | The networking layer shall be transport-agnostic (providers are interchangeable).               | ✅      |
| NFR5  | All source code shall include docstrings and module-level documentation.                       | ✅      |

---

### 4. Constraints and Assumptions

- **Android Focus:** Native hardware APIs (Wi-Fi Direct, Bluetooth) are only
  available on Android via pyjnius. iOS restricts custom P2P socket access.
- **Rust Toolchain Required:** The crypto engine must be compiled from source
  using Cargo and maturin. Pre-built wheels are not distributed.
- **Local Network Assumption:** All peers must be on the same local network
  (or within Bluetooth/Wi-Fi Direct range). There is no internet relay.
- **Single Peer Chat:** The current implementation supports one-to-one chat.
  Group chat is a future enhancement.

---

### 5. Acceptance Criteria

| Criterion                                                        | Verified |
|------------------------------------------------------------------|----------|
| `pytest` test suite passes with all tests green                  | ✅        |
| Application launches on Windows and renders the dark-mode UI     | ✅        |
| Clicking any network mode starts a TCP server and connects       | ✅        |
| Sending a message transmits a `CHAT_MESSAGE` packet over TCP     | ✅        |
| HE ciphertext is sent, computed on blindly, and result returned  | ✅        |
| ZKP keys are generated on startup and displayed in the UI        | ✅        |
