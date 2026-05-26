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

"""Zevy Network Protocol — Newline-delimited JSON packet serialization.

All peer-to-peer communication in Zevy uses this module to serialize and
deserialize packets. Each packet is a single JSON object terminated by a
newline character, enabling simple stream parsing over persistent TCP sockets.
"""

import json

class PacketType:
    """Constants for the packet types exchanged between peers."""
    HANDSHAKE = "HANDSHAKE"
    CHAT_MESSAGE = "CHAT_MESSAGE"
    HE_COMPUTE_REQ = "HE_COMPUTE_REQ"
    HE_COMPUTE_RES = "HE_COMPUTE_RES"

def create_packet(packet_type: str, payload: dict) -> bytes:
    """Serializes a packet to a newline-terminated JSON byte string."""
    data = {
        "type": packet_type,
        "payload": payload
    }
    return (json.dumps(data) + "\n").encode('utf-8')

def parse_packet(raw_line: bytes) -> dict:
    """Deserializes a newline-terminated JSON byte string into a dictionary."""
    return json.loads(raw_line.decode('utf-8').strip())
