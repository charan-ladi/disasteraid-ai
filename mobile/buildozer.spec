[app]

# (str) Title of your application
title = DisasterAid AI

# (str) Package name
package.name = disasteraid

# (str) Package domain (needed for android packaging)
package.domain = org.swecha.disasteraid

# (str) Source code directory
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,requests

# (str) Supported orientations
# Valid values are: landscape, portrait, all or sensible
orientation = portrait

# (bool) Use fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (str) Android API to use
#android.api = 31

# (str) Android NDK to use
#android.ndk = 23b

# (str) Android SDK directory (if empty, it will be automatically downloaded)
#android.sdk_path =

# (str) Android NDK directory (if empty, it will be automatically downloaded)
#android.ndk_path =

# (str) Build profile
build_mode = debug

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1
