class ScheduledSprinklingOfTimerC:

    def when_timer_c_is_operation_(self, operation):
        if operation == "open":
            self.timer_c.open()
        elif operation == "scheduled_open":
            self.timer_c.scheduled_open(3)

    def then_timer_c_should_status_in_3_second(self, status):
        assert status == self.timer_c.get_status()

