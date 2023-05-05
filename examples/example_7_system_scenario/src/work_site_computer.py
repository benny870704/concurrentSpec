import threading, re, waiting, sys
from math import sqrt, acos, pi
from collections import deque
from datetime import datetime
sys.path.append("../../../../../")
from .socket_client import SocketClient
from .serial_client import SerialClient
from .sensor_cone_state import SensorConeState
from .sensor_cone_message_pattern import SensorConeMessagePattern
from .logger import Logger
from .utils import decode_uuid_and_acceleration_from_acceleration_message, decode_uuid_from_startup_message, decode_uuid_and_acceleration_from_stable_message, hex_to_int
from .buzzer import Buzzer

class WorkSiteComputer():
    def __init__(self, socket_client: SocketClient = None, buzzer: Buzzer = None):
        self.uuidToSensorConeData = {}
        self.uuidToHistory = {}
        self.serialList, self.getSerialOutputThreadList = [], []
        self.socket_client = socket_client
        self.buzzer = buzzer
        self.logger = Logger.getLogger(__name__)
        self.processed_message_count = 0
        
    def start(self):
        self.running = True

        for index in range(len(self.serialList)):
            self.getSerialOutputThreadList[index].start()
        
    def terminate(self):
        self.running = False
        if self.socket_client is not None: self.socket_client.close()
        for index in range(len(self.serialList)):
            if self.getSerialOutputThreadList[index].is_alive(): self.getSerialOutputThreadList[index].join()
            self.serialList[index].close()
    
    def __handle_serial_data(self, serial: SerialClient, index: int):
        while self.running:
            if serial.is_open():
                sensorConeMessage = serial.readline()
                if sensorConeMessage is not None:
                    if bool(re.match(SensorConeMessagePattern.ACCELERATION_MESSAGE, sensorConeMessage)):
                        uuid, acceleration = decode_uuid_and_acceleration_from_acceleration_message(sensorConeMessage)
                        self.update_state_by_acceleration(serial, uuid, acceleration)
                    elif bool(re.match(SensorConeMessagePattern.STARTUP_MESSAGE, sensorConeMessage)):
                        uuid = decode_uuid_from_startup_message(sensorConeMessage)
                        self.connect_sensor_cone(uuid)
                        serial.write_flashing_message()
                    self.processed_message_count += 1
            else:
                raise RuntimeError(f"{serial} had been closed.")

    def wait_all_messages_are_processed(self):
        waiting.wait(lambda: self.processed_message_count == (sum(len(serial.get_messages()) for serial in self.serialList))) 

    def attach_serial(self, serialList: list):
        if len(serialList) > 0:
            self.serialList = serialList
            for serial in serialList:
                thread = threading.Thread(target = self.__handle_serial_data, daemon = True, name = f"Serial Manager attached serial {serial}", args = [serial, serialList.index(serial)])
                self.getSerialOutputThreadList.append(thread)

    def connect_sensor_cone(self, uuid: str):
        self.uuidToSensorConeData[uuid] = {'state': SensorConeState.CONNECTED}
        currentTime = datetime.now()
        
        if self.socket_client is not None: self.socket_client.send({"uuid": uuid, "state": SensorConeState.CONNECTED})
        
        self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;36m" + f"{SensorConeState.CONNECTED}" + "\033[0m")
        
    # def __determine_stable_state_by_angle(self, acceleration):
    #     x = float(acceleration[0])
    #     y = float(acceleration[1])
    #     z = float(acceleration[2])
    #     Xg = z / sqrt(x*x + y*y + z*z)
        
    #     angle = round((90 - (acos(Xg)*180.0)/pi), 2)
        
    #     return SensorConeState.FALLEN if angle < -10 else SensorConeState.NORMAL 
        
    # def __determine_unstable_state_by_net_force(self, acceleration):
    #     x = float(acceleration[0])
    #     y = float(acceleration[1])
    #     z = float(acceleration[2])

    #     net_force = abs(sqrt(x ** 2 + y ** 2 + z ** 2))
    
    #     return SensorConeState.MOVING if net_force < 3 else SensorConeState.HITTING
        
    def update_stable_state_by_acceleration(self, uuid:str, acceleration: tuple):
        state = self.__determine_stable_state_by_angle(acceleration)
        if uuid not in self.uuidToSensorConeData:
            self.register_sensor_cone(uuid)
        
        if self.uuidToSensorConeData[uuid]["state"] != SensorConeState.FALLEN and self.uuidToSensorConeData[uuid]["state"] != SensorConeState.NORMAL:
            previousState = self.uuidToSensorConeData[uuid]['state']
            self.uuidToHistory[uuid].append(previousState)
            self.uuidToSensorConeData[uuid]['state'] = state
            if self.socket_client is not None: self.socket_client.send({"uuid": uuid, "state": state})
            currentTime = datetime.now()
            if state == SensorConeState.FALLEN:
                self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;31m" + f"{state}" + "\033[0m")
                self.buzzer.signal()
            elif state == SensorConeState.NORMAL:
                self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;32m" + f"{state}" + "\033[0m")
                self.buzzer.mute()
        
    # def update_unstable_state_by_acceleration(self, uuid: str, acceleration: tuple):
    #     state = self.__determine_unstable_state_by_net_force(acceleration)
    #     if uuid not in self.uuidToSensorConeData:
    #         self.register_sensor_cone(uuid)
        
    #     if state != self.uuidToSensorConeData[uuid]['state'] and self.uuidToSensorConeData[uuid]['state'] != SensorConeState.HITTING:
    #         previousState = self.uuidToSensorConeData[uuid]['state']
    #         self.uuidToHistory[uuid].append(previousState)
    #         self.uuidToSensorConeData[uuid]['state'] = state
            
    #         if self.socket_client is not None: self.socket_client.send({"uuid": uuid, "state": state})
    #         currentTime = datetime.now()
            
    #         if state == SensorConeState.MOVING:
    #             self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;33m" + f"{state}" + "\033[0m")
    #             self.buzzer.mute()
    #         elif state == SensorConeState.HITTING:
    #             self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;35m" + f"{state}" + "\033[0m")
    #             self.buzzer.signal()

    def update_state_by_acceleration(self, serial:SerialClient, uuid: str, acceleration: tuple):
        state = self.__determine_state_by_acceleration(acceleration)
        if uuid not in self.uuidToSensorConeData:
            self.uuidToSensorConeData[uuid] = {'state': None}
            # self.uuidToHistory[uuid] = deque(maxlen = 2)
            # self.uuidToHistory[uuid].append(state)
        # else:
        #     self.uuidToSensorConeData[uuid]['state'] = state
        #     self.uuidToHistory[uuid].append(state)
        
        if self.socket_client is not None: self.socket_client.send({"uuid": uuid, "state": state})
        currentTime = datetime.now()
        if state != self.uuidToSensorConeData.get(uuid).get("state"):
            self.uuidToSensorConeData[uuid]['state'] = state
            if state == SensorConeState.FALLEN:
                self.buzzer.signal()
                serial.write_color_message("red")
                self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;31m" + f"{state}" + "\033[0m")
            elif state == SensorConeState.NORMAL:
                self.buzzer.mute()
                serial.write_color_message("yellow")
                self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;32m" + f"{state}" + "\033[0m")
    
    def __determine_state_by_acceleration(self, acceleration: tuple):
        x = float(acceleration[0])
        y = float(acceleration[1])
        z = float(acceleration[2])
        Xg = z / sqrt(x*x + y*y + z*z)
        angle = round((90 - (acos(Xg)*180.0)/pi), 2)

        return SensorConeState.NORMAL if angle > 50 else SensorConeState.FALLEN

    def check_sensor_cone_exists(self, uuid: str):
        return uuid in self.uuidToSensorConeData

    def get_previous_state_by_uuid(self, uuid: str):
        return self.uuidToHistory[uuid]

    def get_sensor_cone_state_by_uuid(self, uuid: str):
        return self.uuidToSensorConeData[uuid]['state'] if uuid in self.uuidToSensorConeData else None

    def set_sensor_cone_state(self, uuid: str, state: SensorConeState):
        if uuid not in self.uuidToSensorConeData:
            self.register_sensor_cone(uuid, state)
        else:
            self.uuidToSensorConeData[uuid]['state'] = state
        
        currentTime = datetime.now()
        
        if state == SensorConeState.FALLEN:
            self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;31m" + f"{state}" + "\033[0m")
        elif state == SensorConeState.NORMAL:
            self.logger.info("\033[1;30m" + f"[ {currentTime.hour:02}:{currentTime.minute:02}:{currentTime.second:02}:{currentTime.microsecond:0<6} ] " + "\033[0m" + "\033[1;36m" + "[ STATE ]" + "\033[0m" + f" UUID: {uuid}, state: " + "\033[1;32m" + f"{state}" + "\033[0m")
        if self.socket_client is not None: self.socket_client.send({"uuid": uuid, "state": state})
    
    def register_sensor_cone(self, uuid, state = None):
        self.uuidToSensorConeData[uuid] = {'state': '' if state is None else state}
        self.uuidToHistory[uuid] = deque(maxlen = 2)
        self.uuidToHistory[uuid].append('N/A')
        self.uuidToHistory[uuid].append('N/A')
