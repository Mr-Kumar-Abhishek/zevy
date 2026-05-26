import pytest
import asyncio
from network.manager import NetworkManager, NetworkMode

@pytest.mark.asyncio
async def test_network_manager_initialization():
    manager = NetworkManager(mode=NetworkMode.WIFI_DIRECT)
    assert manager.mode == NetworkMode.WIFI_DIRECT
    assert manager.is_running == False

@pytest.mark.asyncio
async def test_network_manager_start_stop():
    manager = NetworkManager(mode=NetworkMode.LOCAL_MDNS_FALLBACK)
    await manager.start()
    assert manager.is_running == True
    await manager.stop()
    assert manager.is_running == False
