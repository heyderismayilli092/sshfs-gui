# sshfs-gui
import sys
from sshfs_gui.app import SSHFSApplication

def main():
    app = SSHFSApplication()
    return app.run(sys.argv)

main()

