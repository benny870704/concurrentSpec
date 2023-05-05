import sys, threading
sys.path.append("../../")
from .serial_client import SerialClient
from .mock_sensor_cone_serial import MockSensorConeSerial
from .real_sensor_cone_serial import RealSensorConeSerial

class SerialManager:

    def __init__(self):
        self.readline_index = 0
        self.serialList, self.messageList = [], []
        self.getSerialOutputThreadList = []
        self.messageIsProcessedEvent = threading.Event()
        self.running = False

    def construct_serial_from_board_list(self, boardList: list):
        if len(boardList) > 0:
            for board in boardList:
                serial = self.__construct_serial(board)
                self.serialList.append(serial)

                thread = threading.Thread(target = self.__handle_serial_data, name = f"Serial Manager constructed serial {serial}", args = [serial])
                self.getSerialOutputThreadList.append(thread)

    def __construct_serial(self, board):
        return MockSensorConeSerial() if board['type'] == "mock" else RealSensorConeSerial(board)

    def attach_serial(self, serialList: list):
        self.running = True

        if len(serialList) > 0:
            self.serialList = serialList
            for serial in serialList:
                thread = threading.Thread(target = self.__handle_serial_data, name = f"Serial Manager attached serial {serial}", args = [serial])
                self.getSerialOutputThreadList.append(thread)
                thread.start()

    def __handle_serial_data(self, serial: SerialClient):
        while self.running:
            if serial.is_open():
                sensorConeMessage = serial.readline()
                if sensorConeMessage is not None:
                    self.messageList.append(sensorConeMessage)
                    self.messageIsProcessedEvent.set()
            else:
                raise RuntimeError(f"{serial} had been closed.")

    def wait_message_is_processed(self):
        self.messageIsProcessedEvent.wait()
        self.messageIsProcessedEvent.clear()

    def wait_all_messages_are_processed(self, count):
        while len(self.messageList) < count: pass

    def read_message(self):
        if len(self.messageList) > self.readline_index:
            self.readline_index += 1
            return self.messageList[self.readline_index - 1]

    def append_message(self, message):
        self.messageList.append(message)

    def get_messages(self):
        return self.messageList

    def close(self):
        if self.running:
            self.running = False

            for index in range(len(self.serialList)):
                self.getSerialOutputThreadList[index].join()
                self.serialList[index].close()
