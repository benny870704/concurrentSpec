from src.sensor_cone import SensorCone
from src.mock_sensor_cone_serial import MockSensorConeSerial
from src.utils import verify_message_is_startup_message

class TurnOnConeC:

    def set_up(self):
        self.uuid = "0000000000000058333733363905041B"

        self.serial_client = MockSensorConeSerial()
        self.sensor_cone = SensorCone(self.uuid, self.serial_client)

    def given_cone_c_is_off(self):
        print("cone1 given_cone_c_is_off")        
        pass

    def when_the_worker_turns_on_cone_c(self):
        print("cone1 when_the_worker_turns_on_cone_c")
        self.sensor_cone.turn_on()
        
    def then_cone_c_is_operational(self):
        # print("cone1 then_cone_c_is_operational")
        
        assert self.sensor_cone.is_open()

    def then_a_registering_message_is_at_the_interface(self):
        # print("cone1 then_a_registering_message_is_at_the_interface_i_cw")
        startup_message = self.serial_client.get_messages()[0]
        
        assert verify_message_is_startup_message(startup_message)

    def tear_down(self):
        self.serial_client.close()

