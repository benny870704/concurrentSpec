import time, threading
from .logger import Logger
from serial import Serial
import serial.tools.list_ports
from .serial_client import SerialClient

class RealSensorConeSerial(SerialClient):
    def __init__(self, board_info: dict):
        self.board_id = board_info["boardId"]
        self.baud_rate = board_info["baudRate"]
        self.device_name = board_info["type"]
        self.readline_index = 0
        self.messages_sent_to_serial = []
        self.messageIsReceivedEvent = threading.Event()
        self.connect()
        
    def __repr__(self) -> str:
        return f"Serial (device_name: {self.device_name}, board_id: {self.board_id})"
        
    def get_serial_type(self):
        return "real"

    def is_open(self):
        return self.serial.isOpen()
    
    def readline(self):
        if len(self.messages_sent_to_serial) > self.readline_index:
            self.readline_index += 1
            return self.messages_sent_to_serial[self.readline_index - 1]

    def send_stop_signal(self):
        self.serial.write(b"StopSerial\n")

    def connect(self):
        self.serial = self.__connect_serial_until_success(self.board_id, self.baud_rate, self.device_name)
        self.__start_reading_message_from_serial()

    def close(self):
        if self.running:
            self.running = False
            self.__stop_reading_message_from_serial()
            self.serial.close()

    def __start_reading_message_from_serial(self):
        self.thread = threading.Thread(target = self.__handle_serial_data)
        self.running = True
        self.thread.start()
        
    def write_flashing_message(self):
        self.serial.write(b"Regist in WSC\n")
        self.messages_sent_to_serial.append("Regist in WSC\n")
        # self.readline_index += 1

    def write_color_message(self, color):
        self.serial.write(f"{color}\n".encode())
        self.messages_sent_to_serial.append(f"{color}\n")
         
    def write_check_message(self):
        self.serial.write(b"Check\n")
        
    def turn_on(self):
        time.sleep(1.75)
        self.serial.write(b"TurnOn\n")

    def __handle_serial_data(self):
        while self.running:
            sensorConeMessage = self.serial.readline().decode('ascii')
            if sensorConeMessage != '':
                self.messages_sent_to_serial.append(sensorConeMessage)

    def __stop_reading_message_from_serial(self):
        self.send_stop_signal()
        self.thread.join()

    def get_messages(self):
        return self.messages_sent_to_serial
    
    def __connect_serial_until_success(self, usbId, baudRate: int, deviceName: str):
        timeout_secound = 15
        serial = self.__connect_serial_by_id(usbId, baudRate)
        while serial is None and timeout_secound > 0:
            print('\033[1;31m' + '[ WARN  ] ' + f'{deviceName} not found. Please check the connection of {deviceName}.' + '\033[0m')
            time.sleep(3)
            serial = self.__connect_serial_by_id(usbId, baudRate)
            timeout_secound -= 3
        
        if serial is None: raise Exception(f"{deviceName} not found.")

        print('\033[1;32m' + '[ INFO  ] ' + f'{deviceName} connected to Work Site Computer successfully.' + '\033[0m')
        return serial
    
    def __connect_serial_by_id(self, usbID: str, baudRate: int):
        for comport in serial.tools.list_ports.comports():
            vid, pid = map(lambda x: int(x, 16), usbID.split(':'))

            if vid == comport.vid and pid == comport.pid:
                return Serial(comport.device, baudRate, timeout=0.5) 
        return None
