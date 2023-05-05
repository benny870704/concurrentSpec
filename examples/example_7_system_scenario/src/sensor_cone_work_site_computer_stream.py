from .serial_client import AbstractDataInterface

class SensorConeWorkSiteComputerStream(AbstractDataInterface):
    def __init__(self):
        self.stream = []
        
    def insert_data(self, data: str):
        if data != None and data != '':
            self.stream.append(data)

    def extract_data(self):
        if len(self.stream) > 0:
            return self.stream.pop(0)
        else:
            return ''

    def get_current_position(self):
        if len(self.stream) > 0:
            return self.stream[0]
        else:
            return ''
        
    def get_last_position(self):
        if len(self.stream) > 0:
            return self.stream[len(self.stream) - 1]
        else:
            return ''

    def check_data_exists(self, data):
        return data in self.stream

    def get_all_messages(self):
        return self.stream