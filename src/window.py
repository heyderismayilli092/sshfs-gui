import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import threading
from gi.repository import Gtk, Gdk, GLib
from handler import Handler


class MainWindow:
    def __init__(self, application):
        builder = Gtk.Builder.new_from_file("ui/mainwindow.ui")
        self.builder = builder

        self.window = builder.get_object("main_window")
        self.window.set_application(application)

        # CSS style
        self.css_code = """
.success {
    color: #2ec27e;
    font-weight: bold;
}
.progress {
    color: #0999f2;
    font-weight: bold;
}
.error {
    color: #e01b24;
    font-weight: bold;
}
.black {
    color: #000;
    font-weight: bold;
}
        """
        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(self.css_code.encode('utf-8'))

        # CSS is being applied globally
        self.display = Gdk.Display.get_default()
        if self.display:
            Gtk.StyleContext.add_provider_for_display(self.display, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # elements
        self.scan_button = builder.get_object("scan_button")
        self.connect_button = builder.get_object("connect_button")
        self.disconnect_button = builder.get_object("disconnect_button")
        self.about_button = builder.get_object("about_button")
        self.device_listbox = builder.get_object("device_listbox")
        self.connected_folders_listbox = builder.get_object("connected_folders_listbox")
        self.host_entry = builder.get_object("host_entry_row")
        self.port_entry = builder.get_object("port_entry_row")
        self.username_entry = builder.get_object("username_entry_row")
        self.password_entry = builder.get_object("password_entry_row")
        self.remote_path_entry = builder.get_object("remote_path_entry_row")
        self.sshscan_pages = builder.get_object("sshscan_pages")
        self.connection_stack = builder.get_object("connection_stack")
        self.sshdeviceslist_button = builder.get_object("sshdeviceslist_button")
        self.connectedfolders_button = builder.get_object("connectedfolders_button")
        self.progressmsj_label = builder.get_object("progressmsj_label")
        self.errormsj_label = builder.get_object("errormsj_label")
        self.connstatus_label = builder.get_object("connstatus_label")
        self.browse_local_folder_button = builder.get_object("browse_local_folder_button")
        self.opt_reconnect_row = builder.get_object("opt_reconnect_row")
        self.opt_allow_other_row = builder.get_object("opt_allow_other_row")
        self.opt_compression_row = builder.get_object("opt_compression_row")
        self.opt_readonly_row = builder.get_object("opt_readonly_row")
        self.opt_serveralive_row = builder.get_object("opt_serveralive_row")
        self.opt_cache_row = builder.get_object("opt_cache_row")
        self.opt_follow_symlinks_row = builder.get_object("opt_follow_symlinks_row")
        self.connection_type_row = builder.get_object("connection_type_row")
        self.remote_source_row = builder.get_object("remote_source_row")
        self.local_mount_point_row = builder.get_object("local_mount_point_row")
        self.options_row = builder.get_object("options_row")
        self.total_size_row = builder.get_object("total_size_row")
        self.used_size_row = builder.get_object("used_size_row")
        self.free_space_row = builder.get_object("free_space_row")
        self.disk_usage_levelbar = builder.get_object("disk_usage_levelbar")
        self.back_connpage = builder.get_object("back_connpage")

        # About Dialog
        self.about_dialog = builder.get_object("about_dialog")

        self.handler = Handler(self)  # handler
        # signals
        self.scan_button.connect("clicked", self.on_scan_clicked)
        self.connectedfolders_button.connect("clicked", self.on_connectedfolders_page)
        self.sshdeviceslist_button.connect("clicked", self.on_sshdeviceslist_page)
        self.browse_local_folder_button.connect("clicked", self.on_select_directory)
        self.connect_button.connect("clicked", self.on_connect)
        self.back_connpage.connect("clicked", self.on_back_connpage)
        self.about_button.connect("clicked", self.on_about)
        self.opt_reconnect_row.connect("notify::active", self.on_opt_reconnect_row)
        self.opt_allow_other_row.connect("notify::active", self.on_opt_allow_other_row)
        self.opt_compression_row.connect("notify::active", self.on_opt_compression_row)
        self.opt_readonly_row.connect("notify::active", self.on_opt_readonly_row)
        self.opt_follow_symlinks_row.connect("notify::active", self.on_opt_follow_symlinks_row)


        # variables
        self.bind_folder = None  # bind folder
        self.sshfs_parameters = []  # sshfs connect parameters
        self.disconnect_button_handlerid = None

    # application gui present
    def show(self):
        output = self.handler.iface_check()
        print("iface: ", output)
        if not output:
            self.scan_button.set_sensitive(False)
            self.connect_button.set_sensitive(False)
        self.window.present()


    # objects CSS style update
    def css_update(self, obj, style):
        obj.set_css_classes([])
        obj.add_css_class(style)
        return True


    # ssh devices scan progress
    def on_scan_clicked(self, button):
        print("Scanning SSH devices...")
        self.progressmsj_label.set_text("Scanning SSH devices...")
        self.sshscan_pages.set_visible_child_name("sshscan_progpage")
        self.sshdeviceslist_button.set_sensitive(False)
        self.scan_button.set_sensitive(False)
        self.connectedfolders_button.set_sensitive(False)
        self.connect_button.set_sensitive(False)
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
        self.connect_button.set_sensitive(True)
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
                self.connected_folders_listbox.append(self.create_connfolders_list(lst))
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
                    self.css_update(self.connstatus_label, "black")
                    self.connstatus_label.set_text("Selected bind folder: '"+self.bind_folder+"'")
        # close the dialog via the main loop
        GLib.idle_add(lambda: (dialog.destroy(), setattr(self, "_req_dialog", None))[0])


    # connect progress
    def on_connect(self, button):
        hostipaddr = self.host_entry.get_text()
        portnumber = self.port_entry.get_text()
        username = self.username_entry.get_text()
        password = self.password_entry.get_text()
        remotepath = self.remote_path_entry.get_text()
        # ip address check
        if not hostipaddr:
            print("Enter a host ip address !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("Enter a host ip address !")
            return False
        else:
            checkip = self.handler.ipaddr_check(hostipaddr)
            if not checkip:
                print("Enter a valid IP address!")
                self.css_update(self.connstatus_label, "error")
                self.connstatus_label.set_text("Enter a valid IP address!")
                return False
        # port number check
        if not portnumber:
            print("Enter a port number !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("Enter a port number !")
            return False
        else:
            if int(portnumber) > 65535:
                print("Enter the correct port number !")
                self.css_update(self.connstatus_label, "error")
                self.connstatus_label.set_text("Enter the correct port number !")
                return False
        # username check
        if not username:
            print("Enter a username !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("Enter a username !")
            return False
        # password check
        if not username:
            print("Enter a password !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("Enter a password !")
            return False
        # check bind folder select
        if not self.bind_folder:
            print("Select the folder to be linked from the computer !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("Select the folder to be linked from the computer !")
            return False
        else:
            checkfolder = self.handler.bindfolder_check(self.bind_folder)
            if not checkfolder:
                print(checkfolder[1])
                self.css_update(self.connstatus_label, "error")
                self.connstatus_label.set_text(checkfolder[1])
                return False
        # remote path check
        if not remotepath:
            print("Enter the folder path on the remote side !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("Enter the folder path on the remote side !")
            return False

        print("Connecting...")
        self.css_update(self.connstatus_label, "progress")
        self.connstatus_label.set_text("Connecting...")
        serveralive_num = self.opt_serveralive_row.get_value()
        if int(serveralive_num) != 0:
            self.sshfs_parameters.append(f"ServerAliveInterval={int(serveralive_num)},")
        sshfs_parameters = "".join(self.sshfs_parameters)
        print("sshfs parameters: ", sshfs_parameters)
        conn_thread = threading.Thread(target=self.connect_progress, daemon=True, args=(username, hostipaddr, remotepath, self.bind_folder, password, sshfs_parameters))
        conn_thread.start()
        return False

    def connect_progress(self, username, host, remote_path, local_path, password, parameters):
        output = self.handler.connect_sshfs(username, host, remote_path, local_path, password, parameters)  # linked folders are being listed
        GLib.idle_add(self.connected_finished, output)

    def connected_finished(self, output):
        if output == True:
            print("Connected successfully !")
            self.css_update(self.connstatus_label, "success")
            self.connstatus_label.set_text("Connected successfully !")
            return False
        else:
            errormsj = output[1]
            print("Error: "+errormsj)
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("Error: "+errormsj)
            return False
    # ------


    # displays information about the mounted folder
    def on_mountpathinfo(self, button, conninfo):
        self.disconnect_button.set_sensitive(True)  # unmount button enable
        # old signal on the unmount button is removed and a new one is written
        if hasattr(self, "disconnect_button_handlerid") and self.disconnect_button_handlerid:
            self.disconnect_button.disconnect(self.disconnect_button_handlerid)
        self.disconnect_button_handlerid = self.disconnect_button.connect("clicked", self.on_unmountpath, conninfo["local_mount_point"])  # unmount button signal
        pathinfo_thread = threading.Thread(target=self.pathinfo_progress, daemon=True, args=(conninfo,))
        pathinfo_thread.start()
        return False

    def pathinfo_progress(self, conninfo):
        local_mountpoint = conninfo["local_mount_point"]
        output_sizeinfo = self.handler.pathsizeinfo(local_mountpoint)
        GLib.idle_add(self.pathinfo_finished, output_sizeinfo, conninfo)

    def pathinfo_finished(self, output_sizeinfo, conninfo):
        if conninfo:
            # printing mounted folder information
            print("Printing folder information...")
            print("source: ", conninfo["remote_source"])
            self.connection_type_row.set_subtitle(conninfo["connection_type"])
            self.remote_source_row.set_subtitle(conninfo["remote_source"])
            self.local_mount_point_row.set_subtitle(conninfo["local_mount_point"])
            self.options_row.set_subtitle(str(conninfo["options"]))
            if output_sizeinfo:
                # path dimension details are being printed
                total_size = str(self.handler.byteformat_size(output_sizeinfo["total"]))
                print("total size: ", total_size)
                used_size = str(self.handler.byteformat_size(output_sizeinfo["used"]))
                print("used size: ", used_size)
                free_space = str(self.handler.byteformat_size(output_sizeinfo["free"]))
                print("free space: ", free_space)
                self.total_size_row.set_subtitle(total_size)
                self.used_size_row.set_subtitle(used_size)
                self.free_space_row.set_subtitle(free_space)
                # it is displayed within the GtkLevelBar
                self.disk_usage_levelbar.set_max_value(output_sizeinfo["total"])
                self.disk_usage_levelbar.set_value(output_sizeinfo["used"])
            else:
                self.total_size_row.set_subtitle("unknown")
                self.used_size_row.set_subtitle("unknown")
                self.free_space_row.set_subtitle("unknown")
            self.connection_stack.set_visible_child_name("info_page")
            print("-"*20)
        else:
            self.connection_stack.set_visible_child_name("conn_page")
            print("The information for the mounted folder could not be displayed !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text("The information for the mounted folder could not be displayed !")
        return False
    # ------


    # connected path unmount
    def on_unmountpath(self, button, mountpath):
        unmount_thread = threading.Thread(target=self.unmount_progress, daemon=True, args=(mountpath,))
        unmount_thread.start()
        return False

    def unmount_progress(self, mountpath):
        output = self.handler.unmount_path(mountpath)
        GLib.idle_add(self.unmount_finished, output, mountpath)

    def unmount_finished(self, output, mountpath):
        if output:
            print(f"'{mountpath}' unmount successfully")
            self.css_update(self.connstatus_label, "success")
            self.connstatus_label.set_text(f"'{mountpath}' unmount successfully")
        else:
            print(f"'{mountpath}' unmount progress failed !")
            self.css_update(self.connstatus_label, "error")
            self.connstatus_label.set_text(f"'{mountpath}' unmount progress failed !")
        self.connection_stack.set_visible_child_name("conn_page")
        self.disconnect_button.set_sensitive(False)
        return False
    # ------


    # back connection page
    def on_back_connpage(self, button):
        self.disconnect_button.set_sensitive(False)
        self.connection_stack.set_visible_child_name("conn_page")
        return False


    # about window
    def on_about(self, button):
        self.about_dialog.present()
        return False

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
    def create_connfolders_list(self, conninfolist):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row_box.set_hexpand(True)
        row_box.set_halign(Gtk.Align.FILL)
        # mount folder title
        label = Gtk.Label(label=conninfolist["local_mount_point"].split("/")[-1])
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        # about button
        about_button = Gtk.Button()
        about_button.set_icon_name("help-about-symbolic")
        about_button.set_tooltip_text("About")
        about_button.connect("clicked", self.on_mountpathinfo, conninfolist)
        # append in box
        row_box.append(label)
        row_box.append(about_button)
        return row_box

    # 'reconnect' parameter
    def on_opt_reconnect_row(self, widget, pspec):
        if widget.get_active():
            print("added new parameter: reconnect")
            self.sshfs_parameters.append("reconnect,")
        else:
            if "reconnect," in self.sshfs_parameters:
                print("removed parameter: reconnect")
                self.sshfs_parameters.remove("reconnect,")

    # 'allow_other' parameter
    def on_opt_allow_other_row(self, widget, pspec):
        if widget.get_active():
            print("added new parameter: allow_other")
            self.sshfs_parameters.append("allow_other,")
        else:
            if "allow_other," in self.sshfs_parameters:
                print("removed parameter: allow_other")
                self.sshfs_parameters.remove("allow_other,")

    # 'compression=yes' parameter
    def on_opt_compression_row(self, widget, pspec):
        if widget.get_active():
            print("added new parameter: compression=yes")
            self.sshfs_parameters.append("compression=yes,")
        else:
            if "compression=yes," in self.sshfs_parameters:
                print("removed parameter: compression=yes")
                self.sshfs_parameters.remove("compression=yes,")

    # 'ro' parameter
    def on_opt_readonly_row(self, widget, pspec):
        if widget.get_active():
            print("added new parameter: ro")
            self.sshfs_parameters.append("ro,")
        else:
            if "ro," in self.sshfs_parameters:
                print("removed parameter: ro")
                self.sshfs_parameters.remove("ro,")

    # 'follow_symlinks' parameter
    def on_opt_follow_symlinks_row(self, widget, pspec):
        if widget.get_active():
            print("added new parameter: follow_symlinks")
            self.sshfs_parameters.append("follow_symlinks,")
        else:
            if "follow_symlinks," in self.sshfs_parameters:
                print("removed parameter: follow_symlinks")
                self.sshfs_parameters.remove("follow_symlinks,")

