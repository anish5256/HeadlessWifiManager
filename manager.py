import platform
from adaptor.win import WindowsWifiManager
from adaptor.rpi import RaspberryPiWifiManager
import os

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
        return os.path.exists('/etc/raspbian_version') or self.check_other_rpi_os_signs()

    def get_manager(self):
        return self.wifi_manager