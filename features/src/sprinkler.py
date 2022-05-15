import time

class Sprinkler:
    def __init__(self, time_of_receiving_signal):
        self.time_of_receiving_signal = time_of_receiving_signal
        self.is_watering = False

    def water(self):
        time.sleep(self.time_of_receiving_signal)
        self.is_watering = True

    def check_watering(self):
        return self.is_watering