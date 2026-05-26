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
from network.manager import NetworkManager, NetworkMode

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
        self.network = NetworkManager()
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
        self.add_peer(f"BT Peer: Android-123 (Simulated)\n[color=#0A84FF]ZKP: {self.zkp_pk[:10]}...[/color]")
        
    def start_wifi_direct_discovery(self):
        import main
        self.network.mode = NetworkMode.WIFI_DIRECT
        asyncio.run_coroutine_threadsafe(self.network.start(), main.network_loop)
        self.add_peer(f"Wi-Fi Peer: Pixel-7 (Simulated)\n[color=#30D158]ZKP: {self.zkp_pk[:10]}...[/color]")
        
    def start_mdns_discovery(self):
        import main
        self.network.mode = NetworkMode.LOCAL_MDNS_FALLBACK
        asyncio.run_coroutine_threadsafe(self.network.start(), main.network_loop)
        self.add_peer(f"Local Node: Laptop (mDNS)\n[color=#FF9F0A]ZKP: {self.zkp_pk[:10]}...[/color]")
        
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
        self.he_client = crypto_rust.HEClient()
        self.server_eval_key = self.he_client.get_evaluation_key()
        self.he_server = crypto_rust.HEServer(self.server_eval_key)
        
    def send_message(self):
        msg = self.ids.message_input_id.text
        if msg:
            self.add_chat_bubble(f"[b]You:[/b] {msg}", is_me=True)
            self.ids.message_input_id.text = ""
            
            # Simulate homomorphic encryption of message truthiness over network
            enc = self.he_client.encrypt_bool(True)
            res = self.he_server.compute_and(enc, enc)
            dec = self.he_client.decrypt_bool(res)
            
            # Simulate received message
            Clock.schedule_once(lambda dt: self.add_chat_bubble(f"[b]Peer:[/b] Got it!\n[size=12][color=#A0A0A0](HE Check: {dec})[/color][/size]", is_me=False), 1.2)
            
    def add_chat_bubble(self, text, is_me):
        bubble = ChatBubble(text=text, is_me=is_me)
        self.ids.chat_log_id.add_widget(bubble)
            
    def go_back(self):
        self.manager.current = 'discovery'
        self.ids.chat_log_id.clear_widgets()
