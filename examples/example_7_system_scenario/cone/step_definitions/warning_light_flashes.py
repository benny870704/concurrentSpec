from src.sensor_cone import SensorCone
from src.mock_sensor_cone_serial import MockSensorConeSerial

class WarningLightFlashes:

    def set_up(self):
        self.uuid = "0000000000000058333733363905041B"

        self.serial_client = MockSensorConeSerial()
        self.sensor_cone = SensorCone(self.uuid, self.serial_client)

    def given_cone_c_is_operational(self):
        self.sensor_cone.turn_on()

    def given_cone_warning_light_is_on(self):
        pass

    def when_a_flashing_message_is_at_the_interface(self):
        flashing_message = self.serial_client.generate_flashing_message()
        self.serial_client.write(flashing_message)

    def then_cone_warning_light_flashes(self):
        assert self.sensor_cone.warning_light_is_flashing()

    def tear_down(self):
        self.serial_client.close()

    def when_a_flashing_message_from_work_site_computer_w_is_at_the_interface(self):
        raise NotImplementedError("when_a_flashing_message_from_work_site_computer_w_is_at_the_interface")

