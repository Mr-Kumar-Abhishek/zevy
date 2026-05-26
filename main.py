import os
import sys
import threading
import asyncio

# Background asyncio loop for network tasks
network_loop = asyncio.new_event_loop()
def run_network_loop():
    asyncio.set_event_loop(network_loop)
    network_loop.run_forever()

threading.Thread(target=run_network_loop, daemon=True).start()

# Ensure Kivy can find everything
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

# Make it look like a mobile phone ratio for Desktop
Window.size = (400, 750)

# Import screens
from ui.screens import DiscoveryScreen, ChatScreen

# Load KV file
Builder.load_file(os.path.join(os.path.dirname(__file__), 'ui', 'components.kv'))

class WindowManager(ScreenManager):
    pass

class ZevyMessengerApp(App):
    def build(self):
        sm = WindowManager(transition=FadeTransition())
        sm.add_widget(DiscoveryScreen(name='discovery'))
        sm.add_widget(ChatScreen(name='chat'))
        return sm

if __name__ == '__main__':
    ZevyMessengerApp().run()
