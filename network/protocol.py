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
