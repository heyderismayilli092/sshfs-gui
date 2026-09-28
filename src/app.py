import gi
gi.require_version("Adw", "1")

from gi.repository import Adw
from window import MainWindow


class SSHFSApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="opensf90.sshfs-gui")

    def do_activate(self):
        if not hasattr(self, "main_window"):
            self.main_window = MainWindow(self)

        self.main_window.show()

