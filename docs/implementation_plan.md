# Secure P2P Kivy Messenger Implementation Plan

This plan outlines the steps required to build the decentralized Kivy messenger with Zero Knowledge Proofs (ZKP), Homomorphic Encryption (HE), Bluetooth, and Wi-Fi Direct capabilities.

> [!CAUTION]
> **User Review Required**
> This project involves highly complex cross-compilation of cryptographic C++ libraries (for ZKP and HE) into Android using Buildozer, as well as low-level Java API bindings via Pyjnius for peer-to-peer networking. This is significantly more difficult than a standard Python/Kivy app. Please review the technical dependencies and constraints below.

## Open Questions

> [!IMPORTANT]
> 1. **Target Platform:** Are we exclusively targeting Android for this initial build? (iOS support for custom Wi-Fi direct and background Bluetooth sockets is extremely restricted and not practically supported via `pyobjus` without native Swift/Objective-C development).
> 2. **Cryptographic Libraries:** Do you have preferred Python libraries for ZKP and HE? Libraries like `TenSEAL` (HE) require complex Android NDK compilation. If pure Python alternatives are preferred (at the cost of performance), please let me know.
> 3. **App Scope:** Building a custom Buildozer recipe for HE libraries can be a project on its own. Would you prefer we start with a simulated cryptographic layer for the UI/Networking MVP, and swap in the heavy C++ cryptography later?

## Proposed Changes

The implementation is broken down into distinct phases.

### Phase 1: Project Setup and Kivy UI
- Initialize the Kivy project structure.
- Build the basic UI: `MainApp`, `DiscoveryScreen`, `ChatScreen`.
- Setup a basic `buildozer.spec` file.

#### [NEW] main.py
#### [NEW] ui/screens.py
#### [NEW] ui/components.kv

---
### Phase 2: Native Android Networking (Pyjnius)
- Implement Python wrappers for Java Android APIs.
- Create asynchronous threads to handle blocking socket connections.

#### [NEW] network/bluetooth_manager.py
- Implements `android.bluetooth.BluetoothAdapter` and socket communication.

#### [NEW] network/wifi_direct_manager.py
- Implements `android.net.wifi.p2p.WifiP2pManager` and broadcast receivers.

---
### Phase 3: Cryptographic Integration
- Integrate ZKP for the peer handshake.
- Integrate HE for private contact discovery.
- (This phase heavily depends on resolving the open questions regarding library choices and Buildozer NDK compilation limits).

#### [NEW] crypto/zkp_engine.py
#### [NEW] crypto/he_engine.py

---
### Phase 4: Integration & Build
- Wire the UI to the networking and crypto backend.
- Refine the `buildozer.spec` to include necessary Android permissions (`BLUETOOTH_CONNECT`, `ACCESS_FINE_LOCATION`, `NEARBY_WIFI_DEVICES`).

#### [MODIFY] main.py
#### [NEW] buildozer.spec

## Verification Plan

### Automated Tests
- Unit testing for the `zkp_engine.py` and `he_engine.py` modules on a desktop environment to verify the mathematical correctness of the protocols.

### Manual Verification
- Deploying the APK to two physical Android devices.
- **Test 1:** Connect via Bluetooth, verify the ZKP handshake succeeds, and exchange messages.
- **Test 2:** Connect via Wi-Fi Direct, verify connection, and exchange messages.
- **Test 3:** Initiate an HE contact matching request and verify the payload is processed correctly without crashing the app.
