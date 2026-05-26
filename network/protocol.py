import json

class PacketType:
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
