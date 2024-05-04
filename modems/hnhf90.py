import requests
from factory.modem_base import ModemBase
from typing import Dict, Any


class HnhF90(ModemBase):
    MODEM_MODEL = "F90"
    BRAND = "H&H"

    def __init__(self, ip_address: str = "192.168.8.1", username: str = "", password: str = "admin"):
        self.base_url = f"http://{ip_address}"
        self.username = username
        self.password = password
        self.session_id = None
        self.modem_status = None
        self.sim_data = None
        self.timeout = 2

    def _login(self) -> bool:
        url = f"{self.base_url}/api/json"
        payload = {
            "fid": "login",
            "username": self.username,
            "password": self.password,
            "sessionId": ""
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": self.base_url,
            "Referer": self.base_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        response = requests.request("POST", url, headers=headers, json=payload, timeout=self.timeout)
        print(response.json())
        if response.status_code == 200:
            self.session_id = response.json()["session"]
            return True
        else:
            return False

    def _get_modem_status(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/json"
        payload = {
            "fid": "queryFields",
            "fields": {
                "simCardState": "invalid",
                "sn": "",
                "imei": "",
                "imsi": "",
                "mac": "",
                "iccId": "",
                "ssidName": "",
                "internetState": "disconnected",
                "signalStrength": "",
                "hardwareVersion": "",
                "systemVersion": "",
                "appVersion": "",
                "wanIpAddress": "",
                "basebandVersion": "",
            },
            "sessionId": self.session_id,
        }
        headers = self._get_headers(url)
        response = requests.request("POST", url, headers=headers, json=payload, timeout=self.timeout)
        if 'reply' in response.json() and response.json()['reply'] == 'Authorization':
            self._login()
            return {}
        if response.status_code == 200:
            return response.json().get("fields", {})
        else:
            return {}

    def _get_sim_data(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/json"
        payload = {
            "fid": "queryApn",
            "fields": {
                "currentApn": "cmnet",
                "apnMode": "auto",
                "currentConfig": "Default",
                "id": -1,
                "selectId": -1,
                "apnConfigs": [{"id": 0, "name": "apn1"}, {"id": 1, "name": "apn2"}],
                "pdpType": "IPv4",
                "configName": "Default",
                "apn": "cmnet",
                "authtype": -1,
                "apnUser": "",
                "apnPassword": "",
            },
            "sessionId": self.session_id,
        }
        headers = self._get_headers(url)
        response = requests.request("POST", url, headers=headers, json=payload, timeout=self.timeout)
        if 'reply' in response.json() and response.json()['reply'] == 'Authorization':
            self._login()
            return {}
        if response.status_code == 200:
            return response.json().get("fields", {})
        else:
            return {}

    def _get_headers(self, url: str) -> Dict[str, str]:
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.session_id,
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": url,
            "Referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

    def _ensure_login(self) -> bool:
        if not self.session_id:
            if not self._login():
                return False
        return True

    def sim_card(self) -> Dict[str, Any]:
        if not self._ensure_login():
            return "Error"

        if self.sim_data is None:
            self.sim_data = self._get_sim_data()

        sim_card = self.sim_data.get("configName", "unknown")
        return sim_card

    def network_strength(self) -> str:
        if not self._ensure_login():
            return "Error"

        if self.modem_status is None:
            self.modem_status = self._get_modem_status()

        network_strength = self.modem_status.get("signalStrength", "unknown")
        return network_strength

    def internet_status(self) -> str:
        if not self._ensure_login():
            return "Error"

        if self.modem_status is None:
            self.modem_status = self._get_modem_status()

        internet = self.modem_status.get("internetState", "unknown")
        return internet

    def get_imei(self) -> str:
        if not self._ensure_login():
            return "Error"

        if self.modem_status is None:
            self.modem_status = self._get_modem_status()

        imei = self.modem_status.get("imei", "unknown")
        return imei

    def get_iccId(self) -> str:
        if not self._ensure_login():
            return "Error"

        if self.modem_status is None:
            self.modem_status = self._get_modem_status()

        icc = self.modem_status.get("iccId", "unknown")
        return icc

    def refresh_data(self):
        if not self._ensure_login():
            return "Error"
        self.modem_status = self._get_modem_status()
        self.sim_data = self._get_sim_data()


# Example usage:
if __name__ == "__main__":
    modem_factory = HnhF90()
    print(modem_factory.sim_card())
    print(modem_factory.network_strength())
