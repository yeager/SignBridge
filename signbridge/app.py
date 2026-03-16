"""GTK4/Adwaita application class for SignBridge."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib

from signbridge import __app_id__, __version__
from signbridge.i18n import _
from signbridge.window import SignBridgeWindow


class SignBridgeApplication(Adw.Application):

    def __init__(self):
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = SignBridgeWindow(application=self)
        win.present()

    def do_startup(self):
        Adw.Application.do_startup(self)
        self._setup_actions()

    def _setup_actions(self):
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

    def _on_about(self, action, param):
        about = Adw.AboutWindow(
            application_name="SignBridge",
            application_icon="camera-video-symbolic",
            version=__version__,
            developer_name="SignBridge Team",
            license_type=Gtk.License.GPL_3_0,
            comments=_("Real-time sign language interpretation via camera"),
            website="https://github.com/yeager/SignBridge",
            transient_for=self.props.active_window,
        )
        about.present()
