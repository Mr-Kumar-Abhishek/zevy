import asyncio
from enum import Enum

class NetworkMode(Enum):
    WIFI_DIRECT = 1
    BLUETOOTH = 2
    LOCAL_MDNS_FALLBACK = 3

class NetworkManager:
    """
    Abstract Network Interface that routes commands through the actual physical connection layers 
    (Wi-Fi Direct, Bluetooth, or local TCP Fallback) without the upper application knowing which is used.
    """
    def __init__(self, mode: NetworkMode = NetworkMode.LOCAL_MDNS_FALLBACK):
        self.mode = mode
        self.is_running = False
        self._provider = None
        self.on_message = None

    async def _handle_provider_message(self, peer_id: str, packet: dict):
        if self.on_message:
            await self.on_message(peer_id, packet)

    async def start(self):
        """Initializes the underlying network listener based on mode"""
        self.is_running = True
        
        if self.mode == NetworkMode.LOCAL_MDNS_FALLBACK:
            from network.mdns_fallback import MDNSFallbackProvider
            self._provider = MDNSFallbackProvider(identifier="zevy_node")
            
        elif self.mode == NetworkMode.WIFI_DIRECT:
            from network.wifi_direct import WiFiDirectProvider
            self._provider = WiFiDirectProvider(identifier="zevy_node")
            
        elif self.mode == NetworkMode.BLUETOOTH:
            from network.bluetooth import BluetoothProvider
            self._provider = BluetoothProvider(identifier="zevy_node")

        if self._provider:
            self._provider.on_message = self._handle_provider_message
            await self._provider.start()
            
        print(f"[Network] Started listening in mode: {self.mode.name}")

    async def stop(self):
        """Stops listeners and tears down connections"""
        self.is_running = False
        if self._provider:
            await self._provider.stop()
        print(f"[Network] Stopped network manager")

    async def broadcast_identity(self, zkp_public_key_hex: str):
        """Broadcasts presence over the localized network"""
        if not self.is_running:
            raise RuntimeError("Network not running")
        print(f"[Network] Broadcasting identity with pubkey length {len(zkp_public_key_hex)}")

    async def discover_peers(self):
        """Listens for peers and initiates handshakes"""
        if not self.is_running:
            raise RuntimeError("Network not running")
        return []

    async def connect_to_peer(self, host: str, port: int) -> str:
        if not self.is_running or not self._provider:
            return None
        if hasattr(self._provider, 'connect_to_peer'):
            return await self._provider.connect_to_peer(host, port)
        return None

    async def send_packet(self, peer_id: str, packet_type: str, payload: dict) -> bool:
        if not self.is_running or not self._provider:
            return False
        if hasattr(self._provider, 'send_packet'):
            return await self._provider.send_packet(peer_id, packet_type, payload)
        return False

_instance = None
def get_network_manager() -> NetworkManager:
    global _instance
    if _instance is None:
        _instance = NetworkManager()
    return _instance
