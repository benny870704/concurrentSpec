import sys, datetime
sys.path.append("../")
from src.sensor_cone import SensorCone
from src.mock_sensor_cone_serial import MockSensorConeSerial
from src.work_site_computer import WorkSiteComputer

class WarningLightFlashesWhenConeCIsTurnedOn:
    def set_up(self):
        self.uuid = "0000000000000058333733363905041B"
        self.serial_client = MockSensorConeSerial()
        self.sensor_cone = SensorCone(self.uuid, self.serial_client)
        self.wsc_uuid = "16fd2706"
        self.work_site_computer = WorkSiteComputer()
        self.work_site_computer.attach_serial([self.serial_client])

    def given_cone_c_connects_to_work_site_computer_w(self):
        pass

    def when_the_current_time_is_t(self):
        self.current_time = datetime.datetime.now()

    def then_the_response_time_is_in_t_1(self):
        assert datetime.datetime.now() - self.current_time <= datetime.timedelta(seconds=1)

    def then_the_response_time_is_in_t_2(self):
        assert datetime.datetime.now() - self.current_time <= datetime.timedelta(seconds=2)

    def tear_down(self):
        self.work_site_computer.terminate()
        self.serial_client.close()

