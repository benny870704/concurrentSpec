from src.sensor_cone_state import SensorConeState
from src.work_site_computer import WorkSiteComputer
from src.mock_sensor_cone_serial import MockSensorConeSerial

class RegisterConeC:

    def set_up(self):
        self.uuid = "0000000000000058333733363905041B"
        self.wsc_uuid = "16fd2706"

        self.serial_client = MockSensorConeSerial()

        self.work_site_computer = WorkSiteComputer()
        self.work_site_computer.attach_serial([self.serial_client])

    def given_work_site_computer_w_is_operational(self):
        # print(f"WSC-> given_work_site_computer_w_is_operational")
        self.work_site_computer.start()
    
    def given_cone_c_is_not_yet_registered(self):
        assert self.work_site_computer.check_sensor_cone_exists(self.uuid) is False
        
    def when_a_registering_message_from_cone_c_is_at_the_interface(self):
        # print(f"WSC-> when_a_registering_message_is_at_the_interface_i_cw")

        startup_message = self.serial_client.generate_startup_message(self.uuid)
        self.serial_client.write(startup_message)

    def then_cone_c_becomes_registered_in_the_work_site_computer_w(self):
        # print(f"WSC-> then_cone_c_becomes_registered_in_the_work_site_computer_w")
        self.work_site_computer.wait_all_messages_are_processed()
        
        assert self.work_site_computer.check_sensor_cone_exists(self.uuid),\
            f"Sensor Cone with uuid: {self.uuid} is not exist"
        assert SensorConeState.CONNECTED == self.work_site_computer.get_sensor_cone_state_by_uuid(self.uuid),\
            f"connected != {self.work_site_computer.get_sensor_cone_state_by_uuid(self.uuid)}"

    def then_a_flashing_message_from_work_site_computer_w_is_at_the_interface(self):
        # print(f"WSC-> then_a_flashing_message_is_at_the_interface_i_cw")

        self.work_site_computer.wait_all_messages_are_processed()
        assert "Regist in WSC\n" in self.serial_client.get_messages()
    
    def tear_down(self):
        self.work_site_computer.terminate()

