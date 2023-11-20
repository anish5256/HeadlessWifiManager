from flask import Flask, render_template, request
from manager import WifiManagerAdapter

app = Flask(__name__)

# Create an instance of the WifiManagerAdapter
wifi_manager = WifiManagerAdapter().get_manager()


@app.route("/")
def index():
    """
    Index route to display the main page.
    It shows available Wi-Fi networks and current network information.
    """
    wifi_networks = wifi_manager.scan_wifi_networks()
    print(wifi_networks)
    current_network_info = wifi_manager.get_current_network_info()
    return render_template(
        "index.html",
        wifi_networks=wifi_networks,
        current_network_info=current_network_info,
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
