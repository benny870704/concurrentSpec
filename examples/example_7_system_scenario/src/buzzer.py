class Buzzer():
    def __init__(self):
        self.mode = "mute"
    
    def buzzer_is_alert(self):
        return self.alert
    
    def signal(self):
        self.mode = "warning"
    
    def mute(self):
        self.mode = "mute"
