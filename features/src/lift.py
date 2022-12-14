class Lift:
    def __init__(self):
        self.stopped_at_a_floor = False
        self.warning_is_given = False
        self.request_is_canceled = False
        self.doors_are_open = False

    def detect_emergency(self, stopped_at_a_floor, warning_is_given, request_is_canceled, doors_are_open):
        self.stopped_at_a_floor = stopped_at_a_floor
        self.warning_is_given = warning_is_given
        self.request_is_canceled = request_is_canceled
        self.doors_are_open = doors_are_open

    def is_stopped_at_a_floor(self):
        return self.stopped_at_a_floor

    def is_warning_given(self):
        return self.warning_is_given

    def is_request_canceled(self):
        return self.request_is_canceled

    def is_doors_open(self):
        return self.doors_are_open
    
