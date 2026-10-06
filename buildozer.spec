[app]
title = Hisabati
package.name = hisabati
package.domain = org.hisabati
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.3.0,sqlite3,arabic-reshaper==3.0.0,python-bidi==0.4.2,six
orientation = portrait
fullscreen = 0
android.api = 33
android.ndk = 25b
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
