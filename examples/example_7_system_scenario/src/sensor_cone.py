from .mock_sensor_cone_serial import MockSensorConeSerial

class SensorCone:
    def __init__(self, uuid: str, serial: MockSensorConeSerial):
        self.uuid = uuid
        self.serial = serial

    def turn_on(self):
        startup_message = self.serial.generate_startup_message(self.uuid)
        self.serial.write(startup_message)

    def send_acceleration_message(self, acceleration: tuple):
        acceleration_message = self.serial.generate_acceleration_message(self.uuid, acceleration)
        self.serial.write(acceleration_message)

    def send_working_message(self):
        working_message = self.serial.generate_working_message(self.uuid)
        self.serial.write(working_message)

    def send_stable_message(self, acceleration: tuple):
        stable_message = self.serial.generate_stable_message(self.uuid, acceleration)
        self.serial.write(stable_message)

    def warning_light_is_flashing(self):
        return True if self.serial.get_messages()[-1] == "Regist in WSC\n" else False
    
    def check_warning_light_color(self, color):
        return True if color in self.serial.get_messages()[-1] else False

    def get_uuid(self):
        return self.uuid
    
    def is_open(self):
        return self.serial.is_open()
