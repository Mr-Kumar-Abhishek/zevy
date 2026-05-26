import sys
import asyncio

if sys.platform == 'android':
    try:
        from jnius import autoclass
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    except Exception as e:
        print(f"[BLE] pyjnius error: {e}")
        BluetoothAdapter = None
else:
    BluetoothAdapter = None

class BluetoothProvider:
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.is_running = False
        self.on_message = None
        self._desktop_fallback = None
        
        if BluetoothAdapter is None:
            # We are on Desktop! Initialize the MDNS Fallback to actually run the ZKP and FHE tests locally.
            print("[BLE] Android BluetoothAdapter unavailable. Using TCP Mock Fallback for Zero-Knowledge & Homomorphic Encryption tests.")
            from network.mdns_fallback import MDNSFallbackProvider
            # Port 8890 for Bluetooth mock so it doesn't collide
            self._desktop_fallback = MDNSFallbackProvider(identifier, port=8890)

    async def start(self):
        self.is_running = True
        if self._desktop_fallback:
            self._desktop_fallback.on_message = self.on_message
            await self._desktop_fallback.start()
            return
            
        print("[BLE] Initializing Native Android Bluetooth layer...")
        self.adapter = BluetoothAdapter.getDefaultAdapter()
        if not self.adapter:
            print("[BLE] No Bluetooth hardware found on Android device")
            return
            
        if not self.adapter.isEnabled():
            print("[BLE] Bluetooth is not enabled")
            
        # Real ServerSocket listening (RFCOMM) would go here
        print("[BLE] Android Native Bluetooth initialized!")

    async def stop(self):
        self.is_running = False
        if self._desktop_fallback:
            await self._desktop_fallback.stop()
            return
        print("[BLE] Stopped Native Bluetooth layer")

    async def connect_to_peer(self, address: str, port: int = 8890) -> str:
        if self._desktop_fallback:
            return await self._desktop_fallback.connect_to_peer(address, port)
            
        print(f"[BLE] Attempting Native Android Bluetooth RFCOMM connection to {address}")
        # Real RFCOMM connect logic goes here
        return None
        
    async def send_packet(self, peer_id: str, packet_type: str, payload: dict) -> bool:
        if self._desktop_fallback:
            return await self._desktop_fallback.send_packet(peer_id, packet_type, payload)
        
        print(f"[BLE] Sending {packet_type} over Native Bluetooth to {peer_id}")
        return False
