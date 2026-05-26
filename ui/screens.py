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

import asyncio
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex

import crypto_rust
from network.manager import get_network_manager, NetworkMode

class PeerButton(Button):
    pass

class ChatBubble(BoxLayout):
    def __init__(self, text, is_me=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 80  # Will auto-size in a real dynamic layout
        
        # Spacer for alignment
        if is_me:
            self.add_widget(Label(size_hint_x=0.2))
            
        bubble = BoxLayout(padding=[15, 10], size_hint_x=0.8)
        
        with bubble.canvas.before:
            if is_me:
                Color(rgba=get_color_from_hex('#0A84FF'))
            else:
                Color(rgba=get_color_from_hex('#2C2C2E'))
            self.rect = RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[15])
            
        bubble.bind(pos=self._update_rect, size=self._update_rect)
        
        lbl = Label(text=text, color=get_color_from_hex('#FFFFFF'), text_size=(None, None), halign='left', valign='center', markup=True)
        lbl.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        lbl.bind(texture_size=lbl.setter('size'))
        
        bubble.add_widget(lbl)
        self.add_widget(bubble)
        
        if not is_me:
            self.add_widget(Label(size_hint_x=0.2))

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class DiscoveryScreen(Screen):
    peer_list = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(DiscoveryScreen, self).__init__(**kwargs)
        self.network = get_network_manager()
        self.peers = []
        
        # Pre-generate Zero-Knowledge Proof keys!
        try:
            self.zkp_pk, self.zkp_vk = crypto_rust.generate_zkp_keys()
        except Exception as e:
            print("ZKP Gen Error:", e)
        
    def start_bluetooth_discovery(self):
        import main
        self.network.mode = NetworkMode.BLUETOOTH
        asyncio.run_coroutine_threadsafe(self.network.start(), main.network_loop)
        
        def delayed_add(*args):
            async def _connect():
                # On desktop, this will hit the fallback on port 8890
                peer_id = await self.network.connect_to_peer('127.0.0.1', 8890)
                if peer_id:
                    Clock.schedule_once(lambda dt: self.add_peer(f"{peer_id} (BLE Fallback)\n[color=#0A84FF]ZKP: {self.zkp_pk[:10]}...[/color]"))
            asyncio.run_coroutine_threadsafe(_connect(), main.network_loop)
        Clock.schedule_once(delayed_add, 1.0)
        
    def start_wifi_direct_discovery(self):
        import main
        self.network.mode = NetworkMode.WIFI_DIRECT
        asyncio.run_coroutine_threadsafe(self.network.start(), main.network_loop)
        
        def delayed_add(*args):
            async def _connect():
                # On desktop, this will hit the fallback on port 8889
                peer_id = await self.network.connect_to_peer('127.0.0.1', 8889)
                if peer_id:
                    Clock.schedule_once(lambda dt: self.add_peer(f"{peer_id} (WiFi Fallback)\n[color=#30D158]ZKP: {self.zkp_pk[:10]}...[/color]"))
            asyncio.run_coroutine_threadsafe(_connect(), main.network_loop)
        Clock.schedule_once(delayed_add, 1.0)
        
    def start_mdns_discovery(self):
        import main
        self.network.mode = NetworkMode.LOCAL_MDNS_FALLBACK
        asyncio.run_coroutine_threadsafe(self.network.start(), main.network_loop)
        
        def delayed_add(*args):
            async def _connect():
                peer_id = await self.network.connect_to_peer('127.0.0.1', 8888)
                if peer_id:
                    Clock.schedule_once(lambda dt: self.add_peer(f"127.0.0.1:8888\n[color=#FF9F0A]ZKP: {self.zkp_pk[:10]}...[/color]"))
            asyncio.run_coroutine_threadsafe(_connect(), main.network_loop)
            
        Clock.schedule_once(delayed_add, 1.0)
        
    def add_peer(self, peer_name):
        self.peers.append(peer_name)
        self.update_peer_list()
        
    def update_peer_list(self):
        grid = self.ids.peer_list
        grid.clear_widgets()
        for p in self.peers:
            btn = PeerButton(text=p, markup=True)
            # Slice out the display name for the chat window
            display_name = p.split('\n')[0]
            btn.bind(on_release=lambda btn, name=display_name: self.connect_to_peer(name))
            grid.add_widget(btn)

    def connect_to_peer(self, peer_info):
        self.manager.current = 'chat'
        chat_screen = self.manager.get_screen('chat')
        chat_screen.current_peer = peer_info

class ChatScreen(Screen):
    current_peer = StringProperty("None")
    message_input = ObjectProperty(None)
    chat_log = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ChatScreen, self).__init__(**kwargs)
        self.network = get_network_manager()
        self.he_client = crypto_rust.HEClient()
        self.server_eval_key = self.he_client.get_evaluation_key()
        self.he_server = crypto_rust.HEServer(self.server_eval_key)
        
    def on_enter(self):
        # Hook up network listener when entering chat
        self.network.on_message = self._on_network_message
        
    async def _on_network_message(self, peer_id, packet):
        import main
        packet_type = packet.get("type")
        payload = packet.get("payload", {})
        
        if packet_type == "CHAT_MESSAGE":
            msg = payload.get("msg", "")
            Clock.schedule_once(lambda dt: self.add_chat_bubble(f"[b]Peer:[/b] {msg}", is_me=False))
            
        elif packet_type == "HE_COMPUTE_REQ":
            cipher_hex = payload.get("cipher")
            # Simulate matching by computing logical AND on the cipher
            res = self.he_server.compute_and(cipher_hex, cipher_hex)
            await self.network.send_packet(peer_id, "HE_COMPUTE_RES", {"res": res})
            
        elif packet_type == "HE_COMPUTE_RES":
            res_hex = payload.get("res")
            dec = self.he_client.decrypt_bool(res_hex)
            Clock.schedule_once(lambda dt: self.add_chat_bubble(f"[size=12][color=#A0A0A0](HE Result computed by peer: {dec})[/color][/size]", is_me=False))

    def send_message(self):
        import main
        msg = self.ids.message_input_id.text
        if msg:
            self.add_chat_bubble(f"[b]You:[/b] {msg}", is_me=True)
            self.ids.message_input_id.text = ""
            
            peer_id = self.current_peer.split('\n')[0] # E.g. "127.0.0.1:8888"
            
            # Send message over socket
            asyncio.run_coroutine_threadsafe(
                self.network.send_packet(peer_id, "CHAT_MESSAGE", {"msg": msg}), main.network_loop
            )
            
            # Send HE challenge over socket
            enc = self.he_client.encrypt_bool(True)
            asyncio.run_coroutine_threadsafe(
                self.network.send_packet(peer_id, "HE_COMPUTE_REQ", {"cipher": enc}), main.network_loop
            )
            
    def add_chat_bubble(self, text, is_me):
        bubble = ChatBubble(text=text, is_me=is_me)
        self.ids.chat_log_id.add_widget(bubble)
            
    def go_back(self):
        self.manager.current = 'discovery'
        self.ids.chat_log_id.clear_widgets()
