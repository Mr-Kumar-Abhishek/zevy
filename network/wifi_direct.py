import sys
import asyncio

if sys.platform == 'android':
    try:
        from jnius import autoclass, cast
        WifiP2pManager = autoclass('android.net.wifi.p2p.WifiP2pManager')
        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
    except Exception as e:
        print(f"[WiFiDirect] pyjnius error: {e}")
        WifiP2pManager = None
else:
    WifiP2pManager = None

class WiFiDirectProvider:
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.is_running = False
        self.on_message = None
        self._desktop_fallback = None
        
        if WifiP2pManager is None:
            # We are on Desktop! Initialize the MDNS Fallback to actually run the ZKP and FHE tests locally.
            print("[WiFiDirect] Android WifiP2pManager unavailable. Using TCP Mock Fallback for Zero-Knowledge & Homomorphic Encryption tests.")
            from network.mdns_fallback import MDNSFallbackProvider
            # Port 8889 for WiFi Direct mock so it doesn't collide with the explicit MDNS provider
            self._desktop_fallback = MDNSFallbackProvider(identifier, port=8889)

    async def start(self):
        self.is_running = True
        if self._desktop_fallback:
            self._desktop_fallback.on_message = self.on_message
            await self._desktop_fallback.start()
            return
            
        # Actual Android implementation
        print("[WiFiDirect] Initializing Native Android P2P connection layer...")
        self.activity = PythonActivity.mActivity
        self.manager = self.activity.getSystemService(Context.WIFI_P2P_SERVICE)
        self.channel = self.manager.initialize(self.activity, self.activity.getMainLooper(), None)
        # Setup BroadcastReceiver for P2P state changes (not fully implemented in MVP to save time)
        print("[WiFiDirect] Android Native WiFi Direct initialized!")

    async def stop(self):
        self.is_running = False
        if self._desktop_fallback:
            await self._desktop_fallback.stop()
            return
        print("[WiFiDirect] Stopped Native P2P connection layer")

    async def connect_to_peer(self, address: str, port: int = 8889) -> str:
        if self._desktop_fallback:
            return await self._desktop_fallback.connect_to_peer(address, port)
            
        print(f"[WiFiDirect] Attempting Native Android connection to peer {address}")
        # Real pyjnius call to WifiP2pConfig and manager.connect() would go here
        return None
        
    async def send_packet(self, peer_id: str, packet_type: str, payload: dict) -> bool:
        if self._desktop_fallback:
            return await self._desktop_fallback.send_packet(peer_id, packet_type, payload)
        
        print(f"[WiFiDirect] Sending {packet_type} over Native Android socket to {peer_id}")
        return False
