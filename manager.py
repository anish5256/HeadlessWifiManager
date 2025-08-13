import platform

from adaptor.mac import MacOSWifiManager
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
        elif self.os_type == 'Darwin':  # Darwin is the system type for macOS
            return MacOSWifiManager()
        else:
            raise NotImplementedError("Unsupported operating system")

    def is_raspberry_pi_os(self):
        # Check for Raspberry Pi hardware
        if os.path.isfile('/proc/device-tree/model'):
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model_info = f.read().lower()
                    if 'raspberry pi' in model_info:
                        return True
            except:
                pass
        
        # Check /etc/os-release for Raspberry Pi OS identifiers
        if os.path.isfile('/etc/os-release'):
            try:
                with open('/etc/os-release', 'r') as f:
                    os_release_content = f.read().lower()
                    # Search for Raspberry Pi OS identifiers
                    if re.search(r'raspbian|raspberry\s*pi|rpi', os_release_content):
                        return True
            except:
                pass
        
        # Check for Raspberry Pi specific files/directories
        rpi_indicators = [
            '/boot/config.txt',
            '/boot/cmdline.txt',
            '/sys/firmware/devicetree/base/model'
        ]
        
        for indicator in rpi_indicators:
            if os.path.exists(indicator):
                try:
                    with open(indicator, 'r') as f:
                        content = f.read().lower()
                        if 'raspberry pi' in content:
                            return True
                except:
                    continue
        
        return False

    def get_manager(self):
        return self.wifi_manager