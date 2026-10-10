# sshfs-gui
import sys
from app import SSHFSApplication

def main():
    app = SSHFSApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()

