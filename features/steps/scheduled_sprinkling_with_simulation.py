from features.src.sprinkler_controller import SprinklerController
from features.src.sprinkler import Sprinkler
from datetime import timedelta
from waiting import wait

class ScheduledSprinklingWithSimulation:
    def __init__(self):
        pass

    def given_three_sprinklers_a_b_and_c(self):
        SPRINKLER_EMITTING_TIME_DELAY = [0.4, 0.3, 0.5]
        self.sprinkler_controller = SprinklerController()
        self.sprinkler_a = Sprinkler(SPRINKLER_EMITTING_TIME_DELAY[0])
        self.sprinkler_b = Sprinkler(SPRINKLER_EMITTING_TIME_DELAY[1])
        self.sprinkler_c = Sprinkler(SPRINKLER_EMITTING_TIME_DELAY[2])
        self.sprinkler_controller.register(self.sprinkler_a)
        self.sprinkler_controller.register(self.sprinkler_b)
        self.sprinkler_controller.register(self.sprinkler_c)

    def given_the_scheduled_time_is_set_to_4_00_00_am(self):
        self.sprinkler_controller.set_scheduled_time("4:00:00")

    def when_the_time_is_4_00_00_am(self):
        self.sprinkler_controller.set_clock_time("4:00:00")

    def then_sprinkler_a_should_emit_water_within_5_seconds(self):
        wait(self.sprinkler_a.check_emitting_water, timeout_seconds=5)
        assert self.sprinkler_controller.get_clock_time() - self.sprinkler_controller.get_scheduled_time() <= timedelta(seconds=5), "sprinkler A timeout"

    def then_sprinkler_b_should_emit_water_within_5_seconds(self):
        wait(self.sprinkler_b.check_emitting_water, timeout_seconds=5)
        assert self.sprinkler_controller.get_clock_time() - self.sprinkler_controller.get_scheduled_time() <= timedelta(seconds=5), "sprinkler B timeout"

    def then_sprinkler_c_should_emit_water_within_5_seconds(self):
        wait(self.sprinkler_c.check_emitting_water, timeout_seconds=5)
        assert self.sprinkler_controller.get_clock_time() - self.sprinkler_controller.get_scheduled_time() <= timedelta(seconds=5), "sprinkler C timeout"

