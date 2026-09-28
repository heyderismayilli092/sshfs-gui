import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk
from handler import Handler


class MainWindow:
    def __init__(self, application):
        builder = Gtk.Builder.new_from_file("ui/mainwindow.ui")
        self.builder = builder

        self.window = builder.get_object("main_window")
        self.window.set_application(application)

        # elements
        self.scan_button = builder.get_object("scan_button")
        self.connect_button = builder.get_object("connect_button")
        self.disconnect_button = builder.get_object("disconnect_button")
        self.device_listbox = builder.get_object("device_listbox")
        self.host_entry = builder.get_object("host_entry_row")
        self.port_entry = builder.get_object("port_entry_row")
        self.username_entry = builder.get_object("username_entry_row")
        self.password_entry = builder.get_object("password_entry_row")
        self.remote_path_entry = builder.get_object("remote_path_entry_row")
        self.local_mount_entry = builder.get_object("local_mount_entry_row")

        self.handler = Handler(self)  # handler
        self.scan_button.connect("clicked", self.handler.on_scan_clicked)

    def show(self):
        self.window.present()

