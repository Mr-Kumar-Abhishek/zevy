import asyncio
import socket
from zeroconf import Zeroconf, ServiceInfo
from network.protocol import parse_packet, create_packet

class MDNSFallbackProvider:
    def __init__(self, identifier: str, port: int = 8888):
        self.identifier = identifier
        self.port = port
        self.is_running = False
        self.zeroconf = None
        self.server = None
        self.active_connections = {} # Dict[str, writer]
        self.on_message = None # async callable(peer_id, packet)

    async def start(self):
        self.is_running = True
        self.zeroconf = Zeroconf()
        
        self.server = await asyncio.start_server(
            self._handle_client, '0.0.0.0', self.port)
            
        print(f"[MDNS] Started local fallback TCP server on port {self.port}")
        
    async def stop(self):
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
        for writer in self.active_connections.values():
            writer.close()
            
        if self.zeroconf:
            self.zeroconf.close()
        print(f"[MDNS] Stopped local fallback server")

    async def _handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        peer_id = f"{addr[0]}:{addr[1]}"
        print(f"[MDNS] Received connection from {peer_id}")
        self.active_connections[peer_id] = writer
        
        try:
            while self.is_running:
                line = await reader.readline()
                if not line:
                    break
                packet = parse_packet(line)
                if self.on_message:
                    await self.on_message(peer_id, packet)
        except Exception as e:
            print(f"[MDNS] Error reading from {peer_id}: {e}")
        finally:
            print(f"[MDNS] Connection closed from {peer_id}")
            if peer_id in self.active_connections:
                del self.active_connections[peer_id]
            writer.close()

    async def connect_to_peer(self, host: str, port: int) -> str:
        peer_id = f"{host}:{port}"
        if peer_id in self.active_connections:
            return peer_id
            
        try:
            reader, writer = await asyncio.open_connection(host, port)
            self.active_connections[peer_id] = writer
            
            # Start a background task to read from this new connection
            asyncio.create_task(self._read_from_peer(peer_id, reader, writer))
            
            return peer_id
        except Exception as e:
            print(f"[MDNS] Failed to connect to {peer_id} - {e}")
            return None
            
    async def _read_from_peer(self, peer_id, reader, writer):
        try:
            while self.is_running:
                line = await reader.readline()
                if not line:
                    break
                packet = parse_packet(line)
                if self.on_message:
                    await self.on_message(peer_id, packet)
        except Exception as e:
            print(f"[MDNS] Error reading from {peer_id}: {e}")
        finally:
            if peer_id in self.active_connections:
                del self.active_connections[peer_id]
            writer.close()

    async def send_packet(self, peer_id: str, packet_type: str, payload: dict) -> bool:
        writer = self.active_connections.get(peer_id)
        if not writer:
            print(f"[MDNS] Cannot send to {peer_id}, not connected.")
            return False
            
        raw_bytes = create_packet(packet_type, payload)
        writer.write(raw_bytes)
        await writer.drain()
        return True
