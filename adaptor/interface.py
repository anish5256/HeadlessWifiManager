import abc

class WifiManagerInterface(abc.ABC):
    """
    Abstract base class to define the interface for WiFi management.
    """

    @abc.abstractmethod
    def scan_wifi_networks(self):
        """
        Scan for available WiFi networks.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abc.abstractmethod
    def connect_to_wifi(self, ssid, password):
        """
        Connect to a WiFi network using given SSID and password.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abc.abstractmethod
    def get_current_network_info(self):
        """
        Get information about the currently connected WiFi network.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abc.abstractmethod
    def load_saved_credentials(self):
        """
        Load saved WiFi credentials.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")
