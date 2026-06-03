[app]
title = Zevy Messenger
package.name = zevy
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = tests,crypto_rust,.venv,.git,docs,.pytest_cache,__pycache__
version = 0.1
requirements = python3,kivy,pyjnius,zeroconf
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, NEARBY_WIFI_DEVICES
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
