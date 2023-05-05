class ScheduledSprinklingOfTimerA:

    def when_timer_a_is_open(self):
        self.timer_a.open()

    def then_timer_a_should_close_in_3_second(self):
        assert "close" == self.timer_a.get_status()

