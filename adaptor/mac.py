import subprocess
import json
import os
import re
import time

from adaptor.interface import WifiManagerInterface


class MacOSWifiManager(WifiManagerInterface):
    def __init__(self):
        self.credentials_file = 'wifi_credentials.json'
        self.airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'

    def scan_wifi_networks(self):
        try:
            scan_output = subprocess.check_output([self.airport_path, '-s'], text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error scanning Wi-Fi networks: {e}")
            return []

        ap_array = []
        for line in scan_output.splitlines()[1:]:  # Skip the first line as it's a header
            # Split the line into components and strip each component
            parts = [part.strip() for part in line.split() if part]
            # The SSID may have spaces, so it is not necessarily the first element after splitting
            # We need to reassemble it considering the fixed position of other columns
            ssid = ' '.join(parts[:-5])
            ap_array.append(ssid)

        return ap_array

    def get_current_network_info(self):
        try:
            info_output = subprocess.check_output([self.airport_path, '-I'], text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error getting current network info: {e}")
            return None

        ssid_regex = re.compile(r'SSID: (.+)')
        ssid_match = ssid_regex.search(info_output)

        ssid = ssid_match.group(1) if ssid_match else 'Not Connected'
        return {'ssid': ssid}

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
        try:
            subprocess.run(['networksetup', '-setairportnetwork', 'en0', ssid, password], check=True)
            self.save_credentials(ssid, password)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to Wi-Fi: {e}")
            return False

    def check_wifi_status(self, timeout=10, interval=1):
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                info_output = subprocess.check_output([self.airport_path, '-I'], text=True)
                if 'state: running' in info_output:
                    return True
                elif 'state: off' in info_output or 'state: init' in info_output:
                    return False
            except subprocess.CalledProcessError as e:
                print(f"Error checking Wi-Fi status: {e}")
                return False

            time.sleep(interval)

        return False
