class Timer:
    def __init__(self, name):
        self.name = name
        self.status = None

    def __repr__(self) -> str:
        return self.name
    
    def open(self):
        self.status = "open"
        # close after 3 second
        self.close()

    def scheduled_open(self, second):
        # print(f"open in {second} seconds")
        self.status = "open"

    def close(self):
        self.status = "close"

    def get_name(self):
        return self.name

    def get_status(self):
        return self.status