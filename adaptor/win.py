import subprocess
import json
import os

class WindowsWifiManager:
    def __init__(self):
        self.credentials_file = 'wifi_credentials.json'

    def scan_wifi_networks(self):
        ap_array = []
        try:
            ap_list = subprocess.check_output("netsh wlan show networks mode=Bssid", shell=True).decode('utf-8', 'ignore')
            for line in ap_list.split('\n'):
                if 'SSID' in line and 'BSSID' not in line:
                    ap_ssid = line.split(': ')[1].strip()
                    ap_array.append(ap_ssid)
        except subprocess.CalledProcessError as e:
            print(f"Error scanning networks: {e}")
        return ap_array

    def connect_to_wifi(self, ssid, password):
        # Create and save a WiFi profile
        profile_xml = self.create_wifi_profile(ssid, password)
        profile_path = f"{ssid}_profile.xml"
        with open(profile_path, 'w') as file:
            file.write(profile_xml)

        try:
            # Add WiFi profile
            subprocess.check_output(f'netsh wlan add profile filename="{profile_path}"', shell=True)
            # Connect to WiFi
            subprocess.check_output(f'netsh wlan connect name="{ssid}"', shell=True)
            self.save_credentials(ssid, password)
            return True
        except subprocess.CalledProcessError:
            return False
        finally:
            # Clean up the profile file
            if os.path.exists(profile_path):
                os.remove(profile_path)

    def create_wifi_profile(self, ssid, password):
        profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        return profile_xml

    def save_credentials(self, ssid, password):
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as file:
                credentials = json.load(file)
        else:
            credentials = {}

        credentials[ssid] = password
        with open(self.credentials_file, 'w') as file:
            json.dump(credentials, file, indent=4)

