import pytest
from network.protocol import create_packet, parse_packet, PacketType

def test_packet_serialization():
    payload = {"msg": "hello world", "he_cipher": "0x1234"}
    raw = create_packet(PacketType.CHAT_MESSAGE, payload)
    
    assert raw.endswith(b"\n")
    
    parsed = parse_packet(raw)
    assert parsed["type"] == PacketType.CHAT_MESSAGE
    assert parsed["payload"]["msg"] == "hello world"
    assert parsed["payload"]["he_cipher"] == "0x1234"
