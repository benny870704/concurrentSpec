from datetime import datetime, timedelta
from features.src.sprinkler_controller import SprinklerController
from features.src.sprinkler import Sprinkler
from testrunner import SPRINKLER_WAITING_MESSAGE_TIME

class ScheduledSprinklingSteps:
    
    def __init__(self):
        self.sprinkler_controller = SprinklerController()
        self.sprinkler_a = Sprinkler(SPRINKLER_WAITING_MESSAGE_TIME[0])

        self.sprinkler_b = Sprinkler(SPRINKLER_WAITING_MESSAGE_TIME[1])
        self.sprinkler_c = Sprinkler(SPRINKLER_WAITING_MESSAGE_TIME[2])
        self.sprinkler_controller.register_sprinkler(self.sprinkler_a)
        self.sprinkler_controller.register_sprinkler(self.sprinkler_b)
        self.sprinkler_controller.register_sprinkler(self.sprinkler_c)

    def given_water_supply_is_normal(self):
        pass

    def given_timer_is_set_to_4_00_00_am(self):
        pass

    def when_the_time_is_4_00_00_am(self):
        self.trigger_time = datetime.now()
        # print("triggered time: ", self.trigger_time.strftime("%H:%M:%S.%f"))
        self.deadline = self.trigger_time + timedelta(seconds=5)
        # print("assertion time: ", self.deadline.strftime("%H:%M:%S.%f"))
        self.sprinkler_controller.trigger_sprinklers()

    def then_sprinkler_a_emits_water_no_later_than_4_00_05_am(self):
        while True:
            timestamp = datetime.now()
            if (timestamp <= self.deadline) and (self.sprinkler_a.check_watering() is True):
                assert self.sprinkler_a.check_watering() is True
                print("sprinkler A passed")
                break
            elif (timestamp > self.deadline):
                assert timestamp <= self.deadline, "sprinkler A timeout"
                assert False

    def then_sprinkler_b_emits_water_no_later_than_4_00_05_am(self):
        while True:
            timestamp = datetime.now()
            if (timestamp <= self.deadline) and (self.sprinkler_b.check_watering() is True):
                assert self.sprinkler_b.check_watering() is True
                print("sprinkler B passed")
                break
            elif (timestamp > self.deadline):
                assert timestamp <= self.deadline, "sprinkler B timeout"
                assert False

    def then_sprinkler_c_emits_water_no_later_than_4_00_05_am(self):
        while True:
            timestamp = datetime.now()
            if (timestamp <= self.deadline) and (self.sprinkler_c.check_watering() is True):
                assert self.sprinkler_c.check_watering() is True
                print("sprinkler C passed")
                break
            elif (timestamp > self.deadline):
                assert timestamp <= self.deadline, "sprinkler C timeout"
                assert False
