# Software Design Document (SDD)
## Secure P2P Messenger

### 1. Introduction
This Software Design Document (SDD) details the architectural choices, system components, and data flows for the secure P2P messenger application built in Kivy.

### 2. System Architecture

#### 2.1 High-Level Architecture
The application follows a modular, multi-threaded architecture to ensure the UI remains responsive during heavy cryptographic processing and blocking network I/O operations.

1. **Presentation Layer (UI):** Built entirely in Kivy, handling user inputs, displaying messages, and managing navigation.
2. **Business Logic Layer:** Manages application state, orchestrates cryptographic handshakes, and handles message queuing.
3. **Cryptography Module:** Encapsulates the complex math required for Zero Knowledge Proofs and Homomorphic Encryption.
4. **Network Access Layer:** Interfaces with native OS APIs for hardware radios (Bluetooth, Wi-Fi).

#### 2.2 Component Design

**A. Kivy Presentation Layer**
- `MainScreen`: Displays active chats and nearby discovered peers.
- `ChatScreen`: The messaging interface for a specific peer.
- `NetworkSettingsScreen`: Toggles between Bluetooth and Wi-Fi Direct modes.

**B. Cryptography Module**
- `ZKP_Engine`: Implements non-interactive zero-knowledge proofs (e.g., using `zksk` or a C++ compiled backend). Used strictly for peer authentication (e.g., proving knowledge of a shared secret without transmitting it).
- `HE_Engine`: Handles Homomorphic Encryption logic. Due to performance constraints on mobile, this will likely use a lightweight scheme (e.g., BFV or CKKS via a compiled wrapper like `TenSEAL`). Used for Private Set Intersection (PSI) to discover mutual contacts securely.

**C. Network Access Layer (Android via Pyjnius)**
- `BluetoothManager`:
  - Uses `android.bluetooth.BluetoothAdapter` and `BluetoothSocket`.
  - Runs a background thread listening via `BluetoothServerSocket`.
- `WiFiDirectManager`:
  - Uses `android.net.wifi.p2p.WifiP2pManager`.
  - Implements a `BroadcastReceiver` via `pyjnius` to handle Wi-Fi state changes and peer discovery intents.
  - Manages standard Java `Socket` connections over the negotiated P2P group owner IP address.

### 3. Data Flow & Protocols

#### 3.1 Peer Discovery & Connection Flow
1. User enables Discovery (Bluetooth or Wi-Fi Direct).
2. `NetworkAccessLayer` activates native OS discovery.
3. OS returns a list of MAC addresses/Device Names.
4. User selects a peer to connect.
5. Sockets are bound, and a continuous byte-stream connection is established.

#### 3.2 Secure Handshake Flow (ZKP)
1. Device A and Device B establish a raw socket.
2. Device A generates a Zero Knowledge Proof to prove its identity (e.g., proving it holds the private key corresponding to a known public identity).
3. Device B verifies the proof mathematically without learning Device A's private key.
4. Device B performs the same proof generation for Device A.
5. Only upon mutual verification does the messaging interface unlock.

#### 3.3 Private Contact Discovery (HE)
1. Device A encrypts its contact list using its HE public key.
2. Device A sends the homomorphically encrypted list to Device B.
3. Device B evaluates a matching function on the encrypted list against its own plaintext contact list.
4. Device B sends the encrypted result back to Device A.
5. Device A decrypts the result to see the intersection, while Device B learns nothing about A's contacts.

### 4. Challenges & Mitigations
- **UI Blocking:** Network sockets are blocking. Mitigation: All Pyjnius socket operations and cryptography must reside in Python `threading.Thread` or Kivy `Clock` asynchronous callbacks.
- **C++ Compilation:** HE and ZKP libraries are computationally heavy and usually written in C++. Mitigation: Heavy reliance on Buildozer recipes and Android NDK cross-compilation.
