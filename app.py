from flask import Flask, render_template, request, session, redirect, url_for
from manager import WifiManagerAdapter

app = Flask(__name__)
app.secret_key = "a813c29bcd06b9a18f3cfc372418e64cb85860a5ebc044a68d59dcbd367233b3"


wifi_manager = WifiManagerAdapter().get_manager()

USERNAME = 'admin'
PASSWORD = 'password'


def is_authenticated():
    return session.get('logged_in', False)


@app.route("/")
def index():
    """
    Index route to display the main page.
    It shows available Wi-Fi networks and current network information.
    """

    if not is_authenticated():
        return render_template('login.html')
    wifi_networks = wifi_manager.scan_wifi_networks()
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



@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == USERNAME and password == PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('success'))
    else:
        return render_template('login.html', error='Invalid username or password')

@app.route('/success')
def success():
    if not is_authenticated():
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))