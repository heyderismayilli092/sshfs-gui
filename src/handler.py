import os
import subprocess
import socket
import re
import ipaddress

class Handler:
    def __init__(self, window):
        self.window = window

    # network ID ip address
    def network_id(self):
        ip = subprocess.check_output(["hostname", "-I"], text=True).split()[0]
        return ip.rsplit(".", 1)[0]

    # scan ssh devices on local network
    def scan_ssh(self):
        devices = []
        for i in range(1, 255):
            ipaddress = self.network_id()+"."+str(i)
            #print(ipaddress)
            try:
                # AF_INET: IPv4, SOCK_STREAM: TCP connection (for SSH)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)  # timeout
                    output = s.connect_ex((ipaddress, 22))
                    if output == 0:
                        devices.append(ipaddress)
            except Exception:
                pass
        #print(devices)
        if devices:
            return devices
        else:
            return False

    # check network connection
    def iface_check(self):
        status = False
        iface = None
        for ifaces in os.listdir("/sys/class/net"):
            try:
                with open(f"/sys/class/net/{ifaces}/operstate", "r") as f:
                    stat = f.read().strip()
                if stat in ["up", "unknown"]:
                    status = True
                    iface = ifaces
                    break
            except FileNotFoundError:
                status = False
                iface = None
        if status:
            return True, iface
        else:
            return False

    # SSHF connections list
    def list_sshfs_mounts(self):
        sshfs_mounts = []
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True, check=True)  # list the active mount points in the system
            for line in result.stdout.splitlines():
                if 'fuse.sshfs' in line or 'sshfs' in line:
                    parts = line.split()
                    if len(parts) >= 5 and parts[1] == 'on':
                        remote_source = parts[0]
                        local_target = parts[2]
                        mount_type = parts[4]
                        options = parts[5].strip('()') if len(parts) > 5 else ""  # if available, get the connection options from inside the parentheses
                        sshfs_mounts.append({
                            "remote_source": remote_source,  # host
                            "local_mount_point": local_target, # connected path
                            "connection_type": mount_type,     # fuse.sshfs
                            "options": options.split(',')      # connected parameters
                        })
            if sshfs_mounts:
                return sshfs_mounts
            else:
                return False
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            return False

    # verifies the accuracy of the entered IP address
    def ipaddr_check(self, ipaddr):
        try:
            checked = ipaddress.ip_address(ipaddr.strip())
            if checked:
                return True
        except ValueError:
            return False

