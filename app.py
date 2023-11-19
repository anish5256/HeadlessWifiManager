from flask import Flask, render_template, request
import subprocess
import os
import time
import shutil

app = Flask(__name__)


import re
import subprocess

def get_current_network_info():
    try:
        iwconfig_output = subprocess.check_output(['iwconfig'], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing iwconfig: {e}")
        return None

    # Parsing logic
    ssid_regex = re.compile(r'ESSID:"(.+?)"')
    quality_regex = re.compile(r'Link Quality=(\d+/\d+)')
    signal_regex = re.compile(r'Signal level=(-?\d+ dBm)')

    ssid_match = ssid_regex.search(iwconfig_output)
    quality_match = quality_regex.search(iwconfig_output)
    signal_match = signal_regex.search(iwconfig_output)

    ssid = ssid_match.group(1) if ssid_match else 'Not Connected'
    quality = quality_match.group(1) if quality_match else 'Unknown'
    signal_strength = signal_match.group(1) if signal_match else 'Unknown'
    data = {
        'ssid': ssid,
        'link_quality': quality,
        'signal_strength': signal_strength
    }

    return data

import json

def load_saved_credentials():
    credentials_file = 'wifi_credentials.json'
    if os.path.exists(credentials_file):
        with open(credentials_file, 'r') as file:
            return json.load(file)
    return {}


@app.route('/')
def index():
    wifi_ap_array = scan_wifi_networks()
    current_network_info = get_current_network_info()
    return render_template('app.html', wifi_ap_array=wifi_ap_array, current_network_info=current_network_info)


@app.route('/save_credentials', methods=['POST'])
def save_credentials():
    ssid = request.form['ssid']
    password = request.form['wifi_key']
    is_connected = connect_to_wifi(ssid, password)
    return render_template('save_credentials.html', ssid=ssid, connection_status=is_connected)


# Function to scan Wi-Fi networks
def scan_wifi_networks():
    iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'ESSID' in line:
            ap_ssid = line[27:-1]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    return ap_array

# Function to connect to a Wi-Fi network
import subprocess


def save_credentials(ssid, password):
    credentials_file = 'wifi_credentials.json'

    # Load existing credentials if the file exists
    if os.path.exists(credentials_file):
        with open(credentials_file, 'r') as file:
            credentials = json.load(file)
    else:
        credentials = {}

    # Update credentials
    credentials[ssid] = password

    # Save back to the file
    with open(credentials_file, 'w') as file:
        json.dump(credentials, file, indent=4)


def connect_to_wifi(ssid, password):
    wpa_supplicant_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    backup_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf.bak'

    # Backup current configuration
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
        #time.sleep(4)
        if check_wifi_status():
            save_credentials(ssid, password)
            return True
        else:
            # Connection unsuccessful, rollback
            shutil.copy(backup_conf_path, wpa_supplicant_conf_path)
            os.system('wpa_cli -i wlan0 reconfigure')
            return False

    finally:
        # Cleanup: remove backup file
        if os.path.exists(backup_conf_path):
            os.remove(backup_conf_path)

def check_wifi_status(timeout=10, interval=2):
    """
    Check the Wi-Fi connection status with a timeout.

    :param timeout: Total time to wait for a successful connection in seconds.
    :param interval: Time interval between status checks in seconds.
    :return: True if connected successfully, False otherwise.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        print("Ok")
        try:
            status_output = subprocess.check_output(['wpa_cli', '-i', 'wlan0', 'status'], text=True)
            print(status_output)

            if 'wpa_state=COMPLETED' in status_output:
                return True  # Connection successful
            elif 'wpa_state=DISCONNECTED' in status_output or 'wpa_state=INTERFACE_DISABLED' in status_output:
                return False  # Connection failed

        except subprocess.CalledProcessError:
            return False  # Command failed

        time.sleep(interval)

    return False  # Timeout reached

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
