from abc import ABC, abstractmethod


class ModemBase(ABC):

    @abstractmethod
    def sim_card(self):
        pass

    @abstractmethod
    def network_strength(self):
        pass

    @abstractmethod
    def internet_status(self):
        pass

    @abstractmethod
    def refresh_data(self):
        pass

    @abstractmethod
    def get_imei(self):
        pass

    @abstractmethod
    def get_iccId(self):
        pass