class EmergencyBrakingAndWarningOverNormalRequests:

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def given_an_outstanding_request_for_lift_to_visit_a_floor(self):
        raise NotImplementedError("given_an_outstanding_request_for_lift_to_visit_a_floor")

    def when_an_emergency_has_been_detected(self):
        raise NotImplementedError("when_an_emergency_has_been_detected")

    def then_lift_is_stopped_at_nearest_floor_in_direction_of_travel(self):
        raise NotImplementedError("then_lift_is_stopped_at_nearest_floor_in_direction_of_travel")

    def then_emergency_indicator_should_be_turned_on(self):
        raise NotImplementedError("then_emergency_indicator_should_be_turned_on")

    def then_the_request_should_be_canceled(self):
        raise NotImplementedError("then_the_request_should_be_canceled")

    def then_lift_doors_should_be_open_within_5_seconds(self):
        raise NotImplementedError("then_lift_doors_should_be_open_within_5_seconds")

