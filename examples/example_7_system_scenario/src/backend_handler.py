class BackendHandler:
    def __init__(self):
        self.is_inserted = False
        
    def insert_data(self):
        self.is_inserted = True
    
    def check_is_inserted(self):
        return self.is_inserted
