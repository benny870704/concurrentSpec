class ScheduledSprinklingOfTimerB:

    def when_timer_b_is_scheduled_to_open(self):
        self.timer_b.scheduled_open(3)

    def then_timer_b_should_open_in_3_second(self):
        assert "open" == self.timer_b.get_status()

