class ScheduledSprinklingOfTimerAAndB:

    def when_timer_a_is_scheduled_to_open(self):
        self.timer_a.scheduled_open(3)

    def when_timer_b_is_open(self):
        self.timer_b.open()

    def then_timer_a_should_open_in_3_second(self):
        assert "open" == self.timer_a.get_status()

    def then_timer_b_should_close_in_3_second(self):
        assert "close" == self.timer_b.get_status()

