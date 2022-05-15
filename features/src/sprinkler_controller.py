from .sprinkler import Sprinkler
from threading import Thread

class SprinklerController:
    def __init__(self):
        self.sprinklers = []
        self.fertilizer_devices = []
    
    def register_sprinkler(self, sprinkler: Sprinkler):
        self.sprinklers.append(sprinkler)

    def trigger_sprinklers(self):
        for sprinkler in self.sprinklers:
            t = Thread(target=sprinkler.water)
            t.setDaemon(True)
            t.start()
            