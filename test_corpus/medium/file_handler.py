
class FileHandler:
    def __init__(self, path):
        self.path = path
        self.file = None
    
    def open(self):
        self.file = open(self.path, 'r')
        return self.file
    
    def close(self):
        if self.file:
            self.file.close()
