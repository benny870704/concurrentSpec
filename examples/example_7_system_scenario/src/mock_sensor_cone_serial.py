import serial, threading, time
from mock_serial import MockSerial
from .serial_client import SerialClient

class MockSensorConeSerial(SerialClient):
    def __init__(self):
        self.messages_sent_to_serial = []
        self.waitMessageIsReadEvent = threading.Event()
        self.readline_index = 0
        
        self.connect()
        self.set_return_message(b"StopSerial\n")
        self.__start_reading_message_from_serial()

    def __repr__(self) -> str:
        return f"Serial (device_name: mock)"

    def get_serial_type(self):
        return "mock"

    def is_open(self):
        return self.serial_client.isOpen()
    
    def readline(self):
        if len(self.messages_sent_to_serial) > self.readline_index:
            self.readline_index += 1
            return self.messages_sent_to_serial[self.readline_index - 1]
    
    def send_stop_signal(self):
        self.serial_client.write(b"StopSerial\n")
    
    def connect(self):
        self.mock_serial = MockSerial()
        self.mock_serial.open()
        self.serial_client = serial.Serial(self.mock_serial.port)
        self.running = True
    
    def close(self):
        if self.running:
            self.running = False
            self.__stop_reading_message_from_serial()
            self.send_stop_signal()
            self.mock_serial.close()

    def get_device_info(self):
        return {"type": "mock"}

    def write_flashing_message(self):
        self.write(self.generate_flashing_message())
    
    def write_color_message(self, color):
        self.write(self.generate_color_message(color))

    def write(self, message):
        self.serial_client.write(message.encode() if type(message) is not bytes else message)
        self.wait_message_is_read()

    def wait_message_is_read(self):
        self.waitMessageIsReadEvent.wait()
        self.waitMessageIsReadEvent.clear()

    def __start_reading_message_from_serial(self):
        self.thread = threading.Thread(target = self.__handle_serial_data, daemon = True, name = "Mock Sensor Cone Serial Thread")
        self.running = True
        self.thread.start()

    def __handle_serial_data(self):
        while self.running:
            sensorConeMessage = self.serial_client.readline().decode('ascii')
            if sensorConeMessage != '':
                self.messages_sent_to_serial.append(sensorConeMessage)
            self.waitMessageIsReadEvent.set()

    def __stop_reading_message_from_serial(self):
        self.send_stop_signal()
        if self.thread.is_alive():
            self.thread.join()

    def get_messages(self):
        return self.messages_sent_to_serial

    def generate_startup_message(self, uuid: str):
        startup_message = f'Startup {uuid}\n'
        self.set_return_message(startup_message)
        return startup_message

    def generate_stable_message(self, uuid:str, acceleration: tuple):
        stable_message = f'Stable {uuid} X: {acceleration[0]} Y: {acceleration[1]} Z: {acceleration[2]}\n'
        self.set_return_message(stable_message)
        time.sleep(2)
        return stable_message
    
    def generate_acceleration_message(self, uuid: str, acceleration: tuple):
        acceleration_message = f'111 Acceleration {uuid} X: {acceleration[0]} Y: {acceleration[1]} Z: {acceleration[2]}\n'
        self.set_return_message(acceleration_message)
        return acceleration_message

    def generate_working_message(self, uuid: str):
        working_message = f'Working {uuid}\n'
        self.set_return_message(working_message)
        return working_message
        
    def generate_flashing_message(self):
        flashing_message = f'Regist in WSC\n'
        self.set_return_message(flashing_message)
        return flashing_message
    
    def generate_color_message(self, color):
        color_message = f'{color}\n'
        self.set_return_message(color_message)
        return color_message
    
    def set_return_message(self, message):
        message = message.encode() if type(message) is not bytes else message
        self.mock_serial.stub(
            receive_bytes = message,
            send_bytes = message
        )
