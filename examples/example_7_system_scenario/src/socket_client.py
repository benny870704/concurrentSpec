import json
import socket

HOST = '0.0.0.0'
PORT = 9999

class SocketClient:

    def __init__(self, ip = HOST, port = PORT):
        self.ip = ip
        self.port = port
        self.connected = False
        self.send_data_index = 0
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sensor_cone_data = []

    def connect(self):
        self.client.connect((self.ip, self.port))
        self.connected = True
        # self.send_temporary_storage_data()

    def send(self, data):
        self.sensor_cone_data.append(data)
        if self.connected:
            try:
                self.client.sendall(json.dumps(data).encode('ascii'))
                self.send_data_index += 1
            except OSError as e:
                print(e)
                self.connected = False

    def send_temporary_storage_data(self):
        if self.connected:
            try:
                while len(self.sensor_cone_data) > self.send_data_index:
                    self.client.sendall(json.dumps(self.sensor_cone_data[self.send_data_index]).encode('ascii'))
                    self.send_data_index += 1
            except OSError as e:
                print(e)
                self.connected = False

    def get_all_data(self):
        return self.sensor_cone_data

    def close(self):
        if self.connected: 
            self.client.shutdown(socket.SHUT_RDWR)
            self.connected = False
        self.client.close()

