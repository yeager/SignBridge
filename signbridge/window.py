"""Main application window for SignBridge."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Gdk

from signbridge.i18n import _
from signbridge.detector import SignDetector


class SignBridgeWindow(Adw.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("SignBridge")
        self.set_default_size(900, 700)

        self._detector = SignDetector()
        self._camera_active = False
        self._frame_timeout_id = None
        self._history = []

        self._build_ui()

    def _build_ui(self):
        # Main layout
        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        # Header bar
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        # About button
        about_btn = Gtk.Button(icon_name="help-about-symbolic")
        about_btn.set_tooltip_text(_("About SignBridge"))
        about_btn.connect("clicked", lambda _: self.get_application().activate_action("about", None))
        header.pack_end(about_btn)

        # Clear history button
        clear_btn = Gtk.Button(icon_name="edit-clear-all-symbolic")
        clear_btn.set_tooltip_text(_("Clear history"))
        clear_btn.connect("clicked", self._on_clear_history)
        header.pack_end(clear_btn)

        # Main content box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        toolbar_view.set_content(main_box)

        # Status banner
        self._status_banner = Adw.Banner()
        self._status_banner.set_title(_("Camera is not active. Press Start to begin."))
        self._status_banner.set_revealed(True)
        main_box.append(self._status_banner)

        # Camera frame
        camera_frame = Gtk.Frame()
        camera_frame.add_css_class("view")
        camera_overlay = Gtk.Overlay()
        camera_frame.set_child(camera_overlay)

        self._camera_image = Gtk.Picture()
        self._camera_image.set_size_request(640, 480)
        self._camera_image.set_content_fit(Gtk.ContentFit.CONTAIN)
        camera_overlay.set_child(self._camera_image)

        # Placeholder when camera is off
        self._camera_placeholder = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        placeholder_icon = Gtk.Image.new_from_icon_name("camera-video-symbolic")
        placeholder_icon.set_pixel_size(64)
        placeholder_icon.add_css_class("dim-label")
        self._camera_placeholder.append(placeholder_icon)
        placeholder_label = Gtk.Label(label=_("Camera preview will appear here"))
        placeholder_label.add_css_class("dim-label")
        placeholder_label.add_css_class("title-3")
        self._camera_placeholder.append(placeholder_label)
        camera_overlay.add_overlay(self._camera_placeholder)

        main_box.append(camera_frame)

        # Current detection - large accessible text
        current_group = Adw.PreferencesGroup()
        current_group.set_title(_("Detected Sign"))

        self._current_label = Gtk.Label(label="—")
        self._current_label.add_css_class("title-1")
        self._current_label.set_selectable(True)
        self._current_label.set_wrap(True)
        self._current_label.set_margin_top(8)
        self._current_label.set_margin_bottom(8)

        current_row = Adw.ActionRow()
        current_row.set_title(_("Current"))
        current_row.add_suffix(self._current_label)
        current_group.add(current_row)
        main_box.append(current_group)

        # History section
        history_group = Adw.PreferencesGroup()
        history_group.set_title(_("History"))

        self._history_label = Gtk.Label(label="")
        self._history_label.set_selectable(True)
        self._history_label.set_wrap(True)
        self._history_label.set_xalign(0)
        self._history_label.set_margin_top(4)
        self._history_label.set_margin_bottom(4)
        self._history_label.set_margin_start(12)
        self._history_label.set_margin_end(12)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(80)
        scrolled.set_max_content_height(150)
        scrolled.set_child(self._history_label)

        history_group.add(scrolled)
        main_box.append(history_group)

        # Control buttons
        button_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
        )
        button_box.set_margin_top(8)

        self._start_btn = Gtk.Button(label=_("Start Camera"))
        self._start_btn.add_css_class("suggested-action")
        self._start_btn.add_css_class("pill")
        self._start_btn.connect("clicked", self._on_start)
        button_box.append(self._start_btn)

        self._stop_btn = Gtk.Button(label=_("Stop Camera"))
        self._stop_btn.add_css_class("destructive-action")
        self._stop_btn.add_css_class("pill")
        self._stop_btn.set_sensitive(False)
        self._stop_btn.connect("clicked", self._on_stop)
        button_box.append(self._stop_btn)

        main_box.append(button_box)

    # -- Camera controls --

    def _on_start(self, btn):
        if self._detector.start_camera():
            self._camera_active = True
            self._start_btn.set_sensitive(False)
            self._stop_btn.set_sensitive(True)
            self._camera_placeholder.set_visible(False)
            self._status_banner.set_title(_("Camera active — show signs to the camera"))
            self._status_banner.add_css_class("success")
            self._frame_timeout_id = GLib.timeout_add(66, self._update_frame)  # ~15 fps
        else:
            self._status_banner.set_title(_("Could not open camera. Check permissions."))
            self._status_banner.remove_css_class("success")

    def _on_stop(self, btn):
        self._camera_active = False
        if self._frame_timeout_id:
            GLib.source_remove(self._frame_timeout_id)
            self._frame_timeout_id = None
        self._detector.stop_camera()
        self._start_btn.set_sensitive(True)
        self._stop_btn.set_sensitive(False)
        self._camera_placeholder.set_visible(True)
        self._status_banner.set_title(_("Camera stopped."))
        self._status_banner.remove_css_class("success")

    def _update_frame(self):
        if not self._camera_active:
            return False

        frame_rgb, detected_sign = self._detector.process_frame()

        if frame_rgb is not None:
            h, w, c = frame_rgb.shape
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                frame_rgb.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                False,
                8,
                w,
                h,
                w * c,
            )
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            self._camera_image.set_paintable(texture)

        if detected_sign:
            self._current_label.set_label(detected_sign)
            if not self._history or self._history[-1] != detected_sign:
                self._history.append(detected_sign)
                self._history_label.set_label(" → ".join(self._history))

        return True

    def _on_clear_history(self, btn):
        self._history.clear()
        self._history_label.set_label("")
        self._current_label.set_label("—")

    def do_close_request(self):
        if self._camera_active:
            self._on_stop(None)
        return False
