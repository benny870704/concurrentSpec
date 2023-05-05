class ScheduledSprinkling:

    def when_timer_timer_is_open(self, timer):
        timer.open()

    def then_timer_timer_should_close_in_3_second(self, timer):
        assert "close" == timer.get_status()

