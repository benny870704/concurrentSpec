from .sprinkler import Sprinkler
import threading
from datetime import datetime, timedelta
from .clock import Clock
class SprinklerController:
    def __init__(self):
        self.sprinklers = []
        self.scheduled_time = datetime.min
        self.is_triggered = False
        self.clock = Clock()
        self.running = True
        self.check_time_thread = threading.Thread(target=self.check_time)
        self.check_time_thread.daemon = True
        self.check_time_thread.start()
        
    def register(self, sprinkler: Sprinkler):
        self.sprinklers.append(sprinkler)

    def set_scheduled_time(self, time_str):
        time = datetime.strptime(time_str, '%H:%M:%S').time()
        self.scheduled_time = datetime.today().replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=0)

    def get_scheduled_time(self):
        return self.scheduled_time
        
    def check_time(self):
        while self.running:
            if self.clock.get_time() >= self.scheduled_time and \
                self.clock.get_time() <= self.scheduled_time + timedelta(minutes=1) and not self.is_triggered:
                self.trigger_sprinklers()
                self.is_triggered = True
                self.running = False
        
    def trigger_sprinklers(self):
        for sprinkler in self.sprinklers:
            t = threading.Thread(target=sprinkler.emit_water)
            t.daemon = True
            t.start()

    def set_clock_time(self, time):
        self.clock.set_time(time)

    def get_clock_time(self):
        return self.clock.get_time()
            