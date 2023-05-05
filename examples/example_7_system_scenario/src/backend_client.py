import requests


class BackendClient:
    def __init__(self, host, port):
        self.domain = f'{host}:{port}'
        
    def register_sensor_cone(self, uuid):
        url = f'http://{self.domain}/smart-cones/{uuid}'
        response = requests.post(url)

        return response
    
    def update_sensor_cone(self, uuid, state):
        url = f'http://{self.domain}/smart-cones/{uuid}'
        payload = {
            "state": state
        }

        response = requests.put(url, json = payload)
        
        return response
