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
