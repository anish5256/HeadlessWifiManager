from flask import Flask, render_template, request, session, redirect, url_for, make_response
from manager import WifiManagerAdapter
import subprocess
import os
import time
import hashlib

from modems.hnhf90 import HnhF90
from modems.interface import ModemDataFetcher

app = Flask(__name__)
app.secret_key = "a813c29bcd06b9a18f3cfc372418e64cb85860a5ebc044a68d59dcbd367233b3"

wifi_manager = WifiManagerAdapter().get_manager()


MODEM_OBJECT = ModemDataFetcher(HnhF90())


USERNAME = 'admin'
PASSWORD = 'password'


def module_in_use_check(module_name):
    # Check if the module is still loaded
    cmd = f"lsmod | grep {module_name}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    return module_name in result.stdout


def generate_auth_token(username):
    # Simple token generation based on username, secret key, and a hash function
    token = hashlib.sha256((username + app.secret_key).encode()).hexdigest()
    return token


def is_authenticated(request):
    auth_token = request.cookies.get('auth_token')
    if auth_token == generate_auth_token(USERNAME):
        return True
    return False


@app.route("/")
def index():
    """
    Index route to display the main page.
    It shows available Wi-Fi networks and current network information.
    """
    if not is_authenticated(request):
        return render_template('login.html')
    wifi_networks = wifi_manager.scan_wifi_networks()
    current_network_info = wifi_manager.get_current_network_info()
    is_setup_mode = module_in_use_check("g_mass_storage")
    return render_template(
        "index.html",
        wifi_networks=wifi_networks,
        current_network_info=current_network_info,
        is_setup_mode=is_setup_mode,
    )


@app.route("/save_credentials", methods=["POST"])
def save_credentials():
    """
    Route to save Wi-Fi credentials.
    Attempts to connect to the specified Wi-Fi network using provided credentials.
    """
    ssid = request.form["ssid"]
    password = request.form["wifi_key"]
    is_connected = wifi_manager.connect_to_wifi(ssid, password)
    current_network_info = wifi_manager.get_current_network_info()
    return render_template(
        "save_credentials.html",
        ssid=ssid,
        connection_status=is_connected,
        current_network_info=current_network_info,
    )


@app.route("/saved_networks")
def saved_networks():
    """
    Route to display saved Wi-Fi networks.
    Shows the networks for which the credentials are saved.
    """
    saved_credentials = wifi_manager.load_saved_credentials()
    return render_template("saved_networks.html", saved_credentials=saved_credentials)


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == USERNAME and password == PASSWORD:
        token = generate_auth_token(username)
        response = make_response(redirect(url_for('index')))
        response.set_cookie('auth_token', token, httponly=True, secure=True)
        return response
    else:
        return render_template('login.html', error='Invalid username or password')


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    response.delete_cookie('auth_token')
    return response


def safely_remove_module(module_name, retry_attempts=3):
    for attempt in range(retry_attempts):
        if not module_in_use_check(module_name):
            print(f"Module {module_name} is not currently loaded.")
            return
        os.system(f'sudo modprobe -r {module_name}')
        time.sleep(1)  # wait a bit before retrying
        if not module_in_use_check(module_name):
            print(f"Module {module_name} unloaded successfully.")
            return
        print(f"Attempt {attempt + 1} failed to unload {module_name}. Retrying...")
    print(f"Failed to unload {module_name} after {retry_attempts} attempts.")


@app.route('/modem_status', methods=['GET'])
def modem_status():
    try:
        status = MODEM_OBJECT.get_data()
        return status
    except Exception as e:
        return {"error": e, "4gSignal": "Error"}


@app.route('/api/setup-mode', methods=['GET'])
def setup_mode():
    state = request.args.get('state')

    if state == 'on':
        try:
            safely_remove_module("g_ether")
            safely_remove_module("g_mass_storage")
            subprocess.run(['sudo', 'modprobe', 'g_mass_storage', 'file=/flash.bin', 'stall=0', 'removable=1'], check=True)
            return 'Setup mode enabled', 200
        except subprocess.CalledProcessError as e:
            return f'Error executing command: {e}', 500
    elif state == 'off':
        # Execute the command as sudo
        try:
            safely_remove_module("g_ether")
            safely_remove_module("g_mass_storage")
            subprocess.run(['sudo', 'modprobe', 'g_ether'],
                           check=True)
            print(print("Hello Disabled"))
            return 'Setup mode disabled', 200
        except subprocess.CalledProcessError as e:
            return f'Error executing command: {e}', 500
    else:
        return 'Invalid state', 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)
