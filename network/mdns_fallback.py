# Zevy Messenger - Peer-to-Peer Encrypted Messaging
# Copyright (c) 2025, Zevy Contributors. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of Zevy nor the names of its contributors may be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""mDNS/TCP Fallback Provider — Local network peer discovery and messaging.

This provider implements the primary desktop networking backend for Zevy.
It runs an async TCP server (using ``asyncio.start_server``) that keeps
persistent connections to peers and exchanges newline-delimited JSON packets.

On Android, the Wi-Fi Direct and Bluetooth providers handle the physical
transport; this module serves as the universal fallback for platforms that
lack native P2P hardware APIs.
"""

import asyncio
import socket
from zeroconf import Zeroconf, ServiceInfo
from network.protocol import parse_packet, create_packet

class MDNSFallbackProvider:
    """Persistent TCP server with async message loops for local P2P.

    Args:
        identifier: A human-readable name for this node.
        port: The TCP port to listen on (default 8888).
    """

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
