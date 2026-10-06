Hisabati | حساباتي - Android (Kivy + SQLite)
Quick test on phone (no build):  install "Pydroid 3" from Google Play, open main.py, then in Pydroid "Pip" install:
  kivy, arabic-reshaper==3.0.0, python-bidi==0.4.2, six   (use the Pydroid repository for kivy), then Run.
Build a real APK:  upload this whole folder (including the hidden .github folder) to a new GitHub repository ->
  Actions tab -> "Build APK" -> download the artifact "Hisabati-APK" -> copy the .apk to the phone -> install.
Data file: accounts.db inside the app's private storage (kept on updates, removed on uninstall).
