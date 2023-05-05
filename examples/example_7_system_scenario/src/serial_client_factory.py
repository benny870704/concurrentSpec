from .mock_sensor_cone_serial import MockSensorConeSerial
from .real_sensor_cone_serial import RealSensorConeSerial

class SerialClientFactory:
    uuid_to_serial_client = {}

    @classmethod
    def create_serial_client(cls, sensor_cone_info):
        uuid = sensor_cone_info["uuid"]
        if uuid in cls.uuid_to_serial_client:
            return cls.uuid_to_serial_client[uuid]
        elif sensor_cone_info["type"] == "real":
            cls.uuid_to_serial_client[uuid] = RealSensorConeSerial(sensor_cone_info)
            return cls.uuid_to_serial_client[uuid]
        elif sensor_cone_info["type"] == "mock":
            cls.uuid_to_serial_client[uuid] = MockSensorConeSerial()
            return cls.uuid_to_serial_client[uuid]

    @classmethod
    def clear(cls):
        cls.uuid_to_serial_client = {}
