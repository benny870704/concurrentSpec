import json
import socket
import threading
from .backend_handler import BackendHandler
from .sensor_cone_state import SensorConeState

bind_ip = "0.0.0.0"
bind_port = 9999

class Backend:
    def __init__(self, backend_handler: BackendHandler = None):
        self.uuidToSensorConeData = {}
        self.postTimes = 0
        self.processed_data_count = 0
        self.socket_server = None
        self.backend_handler = backend_handler
        self.start_getting_request_thread()

    def start_getting_request_thread(self):
        self.running = True
        self.__create_socket_server()
        self.thread = threading.Thread(target = self.__create_connection, daemon = True, name = "Server create connection thread")
        self.thread.start()

    def stop_getting_request_thread(self):
        self.running = False
        if self.socket_server:
            for listening_message_thread in self.listening_message_threads: listening_message_thread.join()
            self.socket_server.close()
        self.thread.join()

    def __create_socket_server(self):
        self.socket_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_server.bind((bind_ip, bind_port))
        self.socket_server.listen(1)
        print(f"[ Backend ] Socket server listening on {bind_ip}:{bind_port}")

    def __create_connection(self):
        self.listening_message_threads = []
        while self.running:
            try:
                client, addr = self.socket_server.accept()
                print(f"[ Backend ] Connected by {addr}")
                thread = threading.Thread(target=self.__listen_message, daemon=True, name=f"Server listening thread by {addr}", args=[client])
                self.listening_message_threads.append(thread)
                thread.start()
            except ConnectionAbortedError:
                print("[ Backend ] Socket server connection aborted")
        
    def __listen_message(self, client: socket):
        while self.running:
            sensor_cone_data = client.recv(1024).decode('ascii')
            if sensor_cone_data != '':
                sensor_cone_data = json.loads(sensor_cone_data)
                self.add_or_update_sensor_cone_data(sensor_cone_data["uuid"], sensor_cone_data["state"])
                self.processed_data_count += 1
        client.close()

    def get_sensor_cone_state(self, uuid: str):
        if uuid in self.uuidToSensorConeData:
            return self.uuidToSensorConeData[uuid][-1]['state']
        else:
            return None

    def check_sensor_cone_exists(self, uuid: str):
        return uuid in self.uuidToSensorConeData

    def add_or_update_sensor_cone_data(self, uuid: str, state: SensorConeState):
        if uuid in self.uuidToSensorConeData:
            self.uuidToSensorConeData[uuid].append({'state': state})
        else:
            self.uuidToSensorConeData[uuid] = [{'state': state}]
        
        self.postTimes += 1

        if self.backend_handler is not None:
            self.backend_handler.insert_data()

    def get_post_times(self):
        return self.postTimes
