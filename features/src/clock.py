from datetime import datetime

class Clock:
    def __init__(self):
        self.time = datetime.now()
        self.real_time = datetime.now()
    
    def set_time(self, time_str):
        time = datetime.strptime(time_str, '%H:%M:%S').time()
        self.time = datetime.today().replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=0)
        self.real_time = datetime.now()

    def get_time(self):
        time = self.time + (datetime.now() - self.real_time)
        return time.replace(microsecond=0)
