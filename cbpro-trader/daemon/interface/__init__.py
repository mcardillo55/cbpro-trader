from .cursesDisplay import cursesDisplay
import threading
from .webNew import Web
from abc import ABC, abstractmethod

class Interface(ABC):
    @staticmethod
    def get_interface(interface_type, indicator_subsys, trade_engine):
        if interface_type == "curses":
            return cursesDisplay(enable=True)
        elif interface_type == "web":
            web_interface = Web(indicator_subsys, trade_engine)
            return web_interface
        else:
            raise ValueError("Invalid Interface type provided")

    @abstractmethod
    def update(self, trade_engine, current_indicators, indicator_period_list, msg):
        return NotImplementedError

    @abstractmethod
    def close(self):
        return NotImplementedError