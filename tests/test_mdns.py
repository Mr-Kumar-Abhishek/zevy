import pytest
import asyncio
from network.mdns_fallback import MDNSFallbackProvider

@pytest.mark.asyncio
async def test_mdns_provider_start_stop():
    provider = MDNSFallbackProvider(identifier="test_node_1")
    await provider.start()
    assert provider.is_running == True
    
    await provider.stop()
    assert provider.is_running == False

@pytest.mark.asyncio
async def test_tcp_peer_exchange():
    # Start two providers locally on different ports
    provider_a = MDNSFallbackProvider(identifier="test_node_A", port=8888)
    provider_b = MDNSFallbackProvider(identifier="test_node_B", port=8889)
    
    await provider_a.start()
    await provider_b.start()
    
    # Provider A connects to Provider B — returns peer_id string on success
    peer_id = await provider_a.connect_to_peer("127.0.0.1", 8889)
    assert peer_id == "127.0.0.1:8889"
    
    await provider_a.stop()
    await provider_b.stop()
