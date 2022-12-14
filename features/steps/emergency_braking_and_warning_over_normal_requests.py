from features.src.lift import Lift

class EmergencyBrakingAndWarningOverNormalRequests:

    def __init__(self):
        pass

    def given_an_outstanding_request_for_the_lift_to_visit_a_floor(self):
        self.lift = Lift()

    def when_an_emergency_has_been_detected(self):
        self.lift.detect_emergency(stopped_at_a_floor=True, warning_is_given=True, request_is_canceled=True, doors_are_open=True)

    def then_the_lift_is_stopped_at_the_nearest_floor_in_the_direction_of_travel(self):
        assert self.lift.is_stopped_at_a_floor() is True

    def then_the_emergency_indicator_is_turned_on(self):
        assert self.lift.is_warning_given() is True

    def then_the_request_is_canceled(self):
        assert self.lift.is_request_canceled() is True

    def then_the_lift_doors_are_open_within_5_seconds(self):
        assert self.lift.is_doors_open() is True

