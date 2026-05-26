# Software Requirement Specification (SRS)
## Secure P2P Messenger

### 1. Introduction

#### 1.1 Purpose
The purpose of this document is to define the software requirements for a highly secure, decentralized, peer-to-peer messenger application. This app is built using Python's Kivy framework and targets mobile devices. It emphasizes extreme privacy by utilizing Zero Knowledge Proofs (ZKP) and Homomorphic Encryption (HE) while operating entirely offline via Bluetooth and Wi-Fi Direct.

#### 1.2 Scope
The application serves as a completely decentralized communication tool. It bypasses traditional centralized servers, internet service providers, and cellular networks by relying exclusively on direct device-to-device radio communication (Bluetooth and Wi-Fi Direct). It introduces advanced cryptography to ensure that identities can be proven without revealing underlying secrets (ZKP) and that operations can be performed on encrypted data (HE).

### 2. Overall Description

#### 2.1 Product Features
1. **Bluetooth Peer-to-Peer Networking:** Direct device-to-device communication without an intermediate router.
2. **Wi-Fi Direct Networking:** Ad-hoc/P2P Wi-Fi connections allowing high-bandwidth data transfer without a central access point.
3. **Zero Knowledge Proofs (ZKP) Authentication:** Users authenticate and establish trust with peers without ever exchanging private keys or passwords over the network.
4. **Homomorphic Encryption (HE) Operations:** Privacy-preserving contact discovery and message operations (e.g., matching common contacts or interests without revealing the contacts themselves to the peer).
5. **Decentralized Chat:** Text-based chat interface.
6. **Cross-Platform UI:** Designed with Kivy for a modern, responsive user interface.

#### 2.2 Operating Environment
- **Primary Target Environment:** Android devices (requires access to native Android Bluetooth and Wi-Fi Direct APIs via Python-for-Android/Pyjnius).
- **Frameworks:** Python 3, Kivy, Buildozer.

#### 2.3 User Classes and Characteristics
- **Privacy Advocates:** Users who demand the highest level of cryptographic security.
- **Off-Grid Users:** Users in areas with limited or compromised internet infrastructure (e.g., natural disasters, remote areas) who need local communication.

### 3. Specific Requirements

#### 3.1 Functional Requirements (FR)
- **FR1 (Bluetooth Discovery):** The app shall scan for and discover nearby devices running the application via Bluetooth.
- **FR2 (Wi-Fi Direct Discovery):** The app shall utilize Wi-Fi Direct to form groups and connect with nearby devices.
- **FR3 (ZKP Handshake):** Upon connection, the app shall execute a Zero Knowledge Proof protocol to verify the identity of the peer before allowing message exchange.
- **FR4 (HE Contact Matching):** The app shall allow users to find mutual contacts using Homomorphic Encryption, ensuring that non-mutual contacts remain perfectly secret.
- **FR5 (Messaging):** The app shall send and receive encrypted text messages over the established P2P sockets.

#### 3.2 Non-Functional Requirements (NFR)
- **NFR1 (Performance):** Cryptographic operations (ZKP generation/verification, HE evaluations) must execute within acceptable timeframes (e.g., < 5 seconds for a handshake) on mobile hardware. Computations must be offloaded to background threads to prevent UI freezing.
- **NFR2 (Security):** All data in transit must be encrypted. Native Android Keystore should be leveraged where possible to protect local secrets.
- **NFR3 (Usability):** The Kivy UI must be intuitive and mask the underlying complexity of the P2P network negotiation.

### 4. Constraints and Assumptions
- **Constraint:** Due to iOS restrictions on custom Wi-Fi Direct and background Bluetooth sockets, the initial implementation will heavily target Android using `pyjnius`.
- **Constraint:** Python-based Homomorphic Encryption libraries (like `TenSEAL` or `Pyfhel`) require compiling C++ backends for ARM64. This will require custom Buildozer recipes.
