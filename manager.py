import platform
from adaptor.win import WindowsWifiManager
from adaptor.rpi import RaspberryPiWifiManager
import os
import re

class WifiManagerAdapter:
    def __init__(self):
        self.os_type = platform.system()
        self.wifi_manager = self.get_wifi_manager()

    def get_wifi_manager(self):
        if self.os_type == 'Windows':
            return WindowsWifiManager()
        elif self.os_type == 'Linux':
            if self.is_raspberry_pi_os():
                return RaspberryPiWifiManager()
            else:
                raise NotImplementedError("Linux OS detected is not Raspberry Pi OS")
        else:
            raise NotImplementedError("Unsupported operating system")

    def is_raspberry_pi_os(self):
        if os.path.isfile('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                os_release_content = f.read()
                # Search for a Raspberry Pi OS identifier in the os-release file
                return re.search(r'raspbian|raspberrypi', os_release_content, re.I) is not None
        return False

    def get_manager(self):
        return self.wifi_manager