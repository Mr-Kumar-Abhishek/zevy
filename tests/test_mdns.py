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
