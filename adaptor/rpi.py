import json
import os
import re
import shutil
import subprocess
import time

from adaptor.interface import WifiManagerInterface


class RaspberryPiWifiManager(WifiManagerInterface):
    def __init__(self):
        self.credentials_file = 'wifi_credentials.json'

    def scan_wifi_networks(self):
        iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
        ap_list, err = iwlist_raw.communicate()
        ap_array = []

        for line in ap_list.decode('utf-8').rsplit('\n'):
            if 'ESSID' in line:
                ap_ssid = line.split(':')[1].strip().replace('"', '')
                if ap_ssid:
                    ap_array.append(ap_ssid)

        return ap_array

    def get_current_network_info(self):
        try:
            iwconfig_output = subprocess.check_output(['iwconfig'], text=True)
            cpuinfo_output = subprocess.check_output(['cat', '/proc/cpuinfo'], text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return None

        ssid_regex = re.compile(r'ESSID:"(.+?)"')
        quality_regex = re.compile(r'Link Quality=(\d+/\d+)')
        signal_regex = re.compile(r'Signal level=(-?\d+ dBm)')
        serial_regex = re.compile(r'Serial\s+:\s+(\w+)')

        ssid_match = ssid_regex.search(iwconfig_output)
        quality_match = quality_regex.search(iwconfig_output)
        signal_match = signal_regex.search(iwconfig_output)
        serial_match = serial_regex.search(cpuinfo_output)

        ssid = ssid_match.group(1) if ssid_match else 'Not Connected'
        quality = quality_match.group(1) if quality_match else 'Unknown'
        signal_strength = signal_match.group(1) if signal_match else 'Unknown'
        serial_number = serial_match.group(1) if serial_match else 'Unknown'

        return {
            'ssid': ssid,
            'link_quality': quality,
            'signal_strength': signal_strength,
            'serial_number': serial_number
        }

    def load_saved_credentials(self):
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as file:
                return json.load(file)
        return {}

    def save_credentials(self, ssid, password):
        credentials = self.load_saved_credentials()
        credentials[ssid] = password

        with open(self.credentials_file, 'w') as file:
            json.dump(credentials, file, indent=4)

    def connect_to_wifi(self, ssid, password):
        wpa_supplicant_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
        backup_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf.bak'
        shutil.copy(wpa_supplicant_conf_path, backup_conf_path)

        conf_content = (
            'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'
            'update_config=1\n\n'
            'network={\n'
            f'    ssid="{ssid}"\n'
            f'    psk="{password}"\n'
            '}'
        )

        try:
            with open(wpa_supplicant_conf_path, 'w') as file:
                file.write(conf_content)

            os.system('wpa_cli -i wlan0 reconfigure')
            if self.check_wifi_status():
                self.save_credentials(ssid, password)
                return True
            else:
                shutil.copy(backup_conf_path, wpa_supplicant_conf_path)
                os.system('wpa_cli -i wlan0 reconfigure')
                return False
        except Exception as e:
            print(e)
        finally:
            if os.path.exists(backup_conf_path):
                os.remove(backup_conf_path)
        return False

    def check_wifi_status(self, timeout=10, interval=1):
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                status_output = subprocess.check_output(['wpa_cli', '-i', 'wlan0', 'status'], text=True)
                print(status_output)
                if 'wpa_state=COMPLETED' in status_output:
                    return True
                elif 'wpa_state=DISCONNECTED' in status_output or 'wpa_state=INTERFACE_DISABLED' in status_output:
                    return False
            except subprocess.CalledProcessError:
                print(subprocess.CalledProcessError)
                return False

            time.sleep(interval)

        return False
