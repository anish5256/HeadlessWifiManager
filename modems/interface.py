from typing import Dict, Any

from factory.modem_base import ModemBase


class ModemDataFetcher:
    def __init__(self, modem: ModemBase):
        self.modem = modem

    def get_data(self) -> Dict[str, Any]:
        data = {}
        self.modem.refresh_data()
        data["sim_card"] = self.modem.sim_card()
        data["4gSignal"] = self.modem.network_strength()
        data["internet"] = self.modem.internet_status()
        data["imei"] = self.modem.get_imei()
        data["iccId"] = self.modem.get_iccId()
        return data
