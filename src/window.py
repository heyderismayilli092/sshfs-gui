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
        self.connected_folders_listbox = builder.get_object("connected_folders_listbox")
        self.host_entry = builder.get_object("host_entry_row")
        self.port_entry = builder.get_object("port_entry_row")
        self.username_entry = builder.get_object("username_entry_row")
        self.password_entry = builder.get_object("password_entry_row")
        self.remote_path_entry = builder.get_object("remote_path_entry_row")
        self.local_mount_entry = builder.get_object("local_mount_entry_row")
        self.sshscan_pages = builder.get_object("sshscan_pages")
        self.sshdeviceslist_button = builder.get_object("sshdeviceslist_button")
        self.connectedfolders_button = builder.get_object("connectedfolders_button")
        self.progressmsj_label = builder.get_object("progressmsj_label")
        self.errormsj_label = builder.get_object("errormsj_label")
        self.connstatus_label = builder.get_object("connstatus_label")
        self.browse_local_folder_button = builder.get_object("browse_local_folder_button")

        self.handler = Handler(self)  # handler
        self.scan_button.connect("clicked", self.on_scan_clicked)
        self.connectedfolders_button.connect("clicked", self.on_connectedfolders_page)
        self.sshdeviceslist_button.connect("clicked", self.on_sshdeviceslist_page)
        self.browse_local_folder_button.connect("clicked", self.on_select_directory)

        # variables
        self.bind_folder = None

    # application gui present
    def show(self):
        output = self.handler.iface_check()
        print("iface: ", output)
        if not output:
            self.scan_button.set_sensitive(False)
            self.connect_button.set_sensitive(False)
        self.window.present()

    # ssh devices scan progress
    def on_scan_clicked(self, button):
        print("Scanning SSH devices...")
        self.progressmsj_label.set_text("Scanning SSH devices...")
        self.sshscan_pages.set_visible_child_name("sshscan_progpage")
        self.sshdeviceslist_button.set_sensitive(False)
        self.scan_button.set_sensitive(False)
        self.connectedfolders_button.set_sensitive(False)
        sshscan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        sshscan_thread.start()
        return False

    def scan_worker(self):
        addresslist = self.handler.scan_ssh()  # ssh scan progress
        GLib.idle_add(self.scan_finished, addresslist)

    def scan_finished(self, addresslist):
        self.sshdeviceslist_button.set_sensitive(True)
        self.scan_button.set_sensitive(True)
        self.connectedfolders_button.set_sensitive(True)
        print("Devices: ", addresslist)
        if addresslist:
            for lst in addresslist:
                self.device_listbox.append(self.create_line_label(lst))
            self.sshscan_pages.set_visible_child_name("sshscan_page")
        else:
            self.errormsj_label.set_text("SSH devices not found")
            self.sshscan_pages.set_visible_child_name("errorpage")
        return False
    # ------

    # list connected folders
    def on_connectedfolders_page(self, button):
        print("Listing connected folders...")
        self.progressmsj_label.set_text("Listing connected folders...")
        self.sshscan_pages.set_visible_child_name("sshscan_progpage")
        connfolders_thread = threading.Thread(target=self.list_connected, daemon=True)
        connfolders_thread.start()
        return False

    def list_connected(self):
        connlist = self.handler.list_sshfs_mounts()  # linked folders are being listed
        GLib.idle_add(self.list_finished, connlist)

    def list_finished(self, connlist):
        if connlist:
            print(connlist)
            # check list
            if self.connected_folders_listbox:
                while child := self.connected_folders_listbox.get_first_child():
                    self.connected_folders_listbox.remove(child)
            for lst in connlist:
                self.connected_folders_listbox.append(self.create_connfolders_list(lst["local_mount_point"].split("/")[-1]))
            self.sshscan_pages.set_visible_child_name("connectedfolders_page")
        else:
            self.errormsj_label.set_text("Connected folders not found")
            self.sshscan_pages.set_visible_child_name("errorpage")
        return False
    # ------

    # SSH devices page
    def on_sshdeviceslist_page(self, button):
        self.sshscan_pages.set_visible_child_name("sshscan_page")
        return False

    # select bind folder
    def on_select_directory(self, button):
        # we keep the dialog within `self` to prevent early garbage collection
        self._req_dialog = Gtk.FileChooserNative(
            title="Choose connection folder",
            transient_for=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            accept_label="Select",
            cancel_label="Cancel"
        )
        # response handler
        self._req_dialog.connect("response", self.on_dir_response)
        self._req_dialog.show()

    def on_dir_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            folder = dialog.get_file()
            if folder is not None:
                path = folder.get_path()
                if path:
                    self.bind_folder = path
                    print("Selected bind folder:", self.bind_folder)
        # close the dialog via the main loop
        GLib.idle_add(lambda: (dialog.destroy(), setattr(self, "_req_dialog", None))[0])


    # function(s) that create objects for GtkListBox rows
    # enables the listing of discovered SSH devices
    def create_line_label(self, text):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        # label
        label = Gtk.Label(xalign=0)
        label.set_label(text)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        # append in box
        hbox.append(label)
        hbox.set_margin_top(6)
        hbox.set_margin_bottom(6)
        hbox.set_margin_start(6)
        hbox.set_margin_end(6)
        return hbox

    # enables listing of linked folders
    def create_connfolders_list(self, text):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row_box.set_hexpand(True)
        row_box.set_halign(Gtk.Align.FILL)
        # mount folder title
        label = Gtk.Label(label=text)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        # about button
        about_button = Gtk.Button()
        about_button.set_icon_name("help-about-symbolic")
        about_button.set_tooltip_text("About")
        # unmount button
        umount_button = Gtk.Button()
        umount_button.set_icon_name("media-eject-symbolic")
        umount_button.set_tooltip_text("Unmount")
        # append in box
        row_box.append(label)
        row_box.append(about_button)
        row_box.append(umount_button)
        return row_box


