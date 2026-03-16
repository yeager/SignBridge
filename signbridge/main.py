"""Main entry point for SignBridge application."""

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gio

from signbridge import __app_id__
from signbridge.i18n import _
from signbridge.app import SignBridgeApplication


def main():
    app = SignBridgeApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
