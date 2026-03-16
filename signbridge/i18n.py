"""Internationalization setup for SignBridge."""

import gettext
import locale
import os

APP_NAME = "signbridge"

localedir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "po", "locale")
if not os.path.isdir(localedir):
    localedir = os.path.join(sys.prefix, "share", "locale") if "sys" in dir() else localedir

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

import sys

for loc_dir in [
    localedir,
    os.path.join(sys.prefix, "share", "locale"),
    "/usr/share/locale",
]:
    if os.path.isdir(loc_dir):
        localedir = loc_dir
        break

translation = gettext.translation(APP_NAME, localedir=localedir, fallback=True)
_ = translation.gettext
