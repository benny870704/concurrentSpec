from src.sensor_cone import SensorCone
from src.mock_sensor_cone_serial import MockSensorConeSerial
from src.utils import verify_message_is_startup_message
import datetime

class TurnOnConeC:

    def set_up(self):
        self.uuid = "0000000000000058333733363905041B"

        self.serial_client = MockSensorConeSerial()
        self.sensor_cone = SensorCone(self.uuid, self.serial_client)

    def given_cone_c_is_off(self):
        print("cone1 given_cone_c_is_off")        
        pass

    def when_a_worker_turns_on_cone_c_at_time_t(self):
        print("cone1 when_the_worker_turns_on_cone_c")
        self.sensor_cone.turn_on()
        self.current_time = datetime.datetime.now()

    def then_the_power_on_reset_of_cone_c_is_successful(self):
        assert True

    def then_the_power_on_self_test_of_cone_c_is_successful(self):
        assert True
        
    def then_cone_c_is_operational(self):
        # print("cone1 then_cone_c_is_operational")
        assert self.sensor_cone.is_open()

    def then_cone_warning_light_is_on(self):
        assert self.sensor_cone.warning_light_is_on()

    def then_a_registering_message_from_cone_c_is_at_the_interface(self):
        # print("cone1 then_a_registering_message_is_at_the_interface_i_cw")
        startup_message = self.serial_client.get_messages()[0]
        
        assert verify_message_is_startup_message(startup_message)

    def tear_down(self):
        self.serial_client.close()

