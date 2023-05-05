import sys
sys.path.append("../../../../../")
from abc import abstractmethod
# from exploratoryTool.src.connection_domain import ConnectionDomainABC

class SerialClient:

    @abstractmethod
    def get_serial_type(self):
        pass

    @abstractmethod
    def is_open(self):
        pass

    @abstractmethod
    def readline(self):
        pass
    
    @abstractmethod
    def write_flashing_message(self):
        pass
    
    @abstractmethod
    def write_color_message(self):
        pass
    
    @abstractmethod
    def send_stop_signal(self):
        pass

    @abstractmethod
    def get_messages(self):
        pass
    
    @abstractmethod
    def close(self):
        pass
