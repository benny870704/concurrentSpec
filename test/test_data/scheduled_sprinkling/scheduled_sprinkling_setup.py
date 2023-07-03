from test.test_data.timer import Timer

class ScheduledSprinklingSetup:

    def given_timer_a(self):
        self.timer_a = Timer("timer_a")

    def given_timer_b(self):
        self.timer_b = Timer("timer_b")

    def given_timer_c(self):
        self.timer_c = Timer("timer_c")


