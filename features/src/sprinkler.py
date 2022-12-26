import time
from datetime import timedelta
from .clock import Clock

class Sprinkler:
    def __init__(self, time_of_receiving_signal=0):
        self.time_of_receiving_signal = time_of_receiving_signal
        self.is_emitting_water = False

    def emit_water(self):
        time.sleep(self.time_of_receiving_signal)
        self.is_emitting_water = True

    def check_emitting_water(self):
        return self.is_emitting_water
