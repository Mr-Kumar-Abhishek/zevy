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

"""Zevy Messenger — Entry point.

Launches a background asyncio event loop for non-blocking network I/O,
then starts the Kivy application with the ScreenManager containing
the DiscoveryScreen and ChatScreen.
"""

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
