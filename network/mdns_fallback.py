import asyncio
import socket
from zeroconf import Zeroconf, ServiceInfo

class MDNSFallbackProvider:
    def __init__(self, identifier: str, port: int = 8888):
        self.identifier = identifier
        self.port = port
        self.is_running = False
        self.zeroconf = None
        self.server = None

    async def start(self):
        self.is_running = True
        self.zeroconf = Zeroconf()
        
        # Start TCP server
        self.server = await asyncio.start_server(
            self._handle_client, '0.0.0.0', self.port)
            
        print(f"[MDNS] Started local fallback TCP server on port {self.port}")
        
    async def stop(self):
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        if self.zeroconf:
            self.zeroconf.close()
        print(f"[MDNS] Stopped local fallback server")

    async def _handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"[MDNS] Received connection from {addr}")
        writer.close()
        await writer.wait_closed()

    async def connect_to_peer(self, host: str, port: int) -> bool:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return True
        except Exception as e:
            print(f"[MDNS] Failed to connect to {host}:{port} - {e}")
            return False
