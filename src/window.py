import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import threading
from gi.repository import Gtk, GLib
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
        self.sshscan_pages = builder.get_object("sshscan_pages")
        self.sshdeviceslist_button = builder.get_object("sshdeviceslist_button")
        self.connectedfolders_button = builder.get_object("connectedfolders_button")

        self.handler = Handler(self)  # handler
        self.scan_button.connect("clicked", self.on_scan_clicked)
        self.connectedfolders_button.connect("clicked", self.on_connectedfolder_page)
        self.sshdeviceslist_button.connect("clicked", self.on_sshdeviceslist_page)

    # application gui present
    def show(self):
        output = self.handler.iface_check()
        if not output:
            self.scan_button.set_sensitive(False)
            self.connect_button.set_sensitive(False)
        self.window.present()

    # ssh devices scan progress
    def on_scan_clicked(self, button):
        self.sshscan_pages.set_visible_child_name("sshscan_page2")
        sshscan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        sshscan_thread.start()
        return False

    def scan_worker(self):
        addresslist = self.handler.scan_ssh()  # ssh scan progress
        GLib.idle_add(self.scan_finished, addresslist)

    def scan_finished(self, addresslist):
        for lst in addresslist:
            self.device_listbox.append(self.create_line_label(lst))
        self.sshscan_pages.set_visible_child_name("sshscan_page")
        return False
    # ------

    # Connected Folders page
    def on_connectedfolder_page(self, button):
        self.sshscan_pages.set_visible_child_name("connected_folders")
        return False

    # SSH devices page
    def on_sshdeviceslist_page(self, button):
        self.sshscan_pages.set_visible_child_name("sshscan_page")
        return False


    # function(s) that create objects for GtkListBox rows
    def create_line_label(self, text):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        # label
        label = Gtk.Label(xalign=0)
        label.set_label(text)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        hbox.append(label)
        hbox.set_margin_top(6)
        hbox.set_margin_bottom(6)
        hbox.set_margin_start(6)
        hbox.set_margin_end(6)
        return hbox

