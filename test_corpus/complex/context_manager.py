
class Database:
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def connect(self): pass
    def close(self): pass
    def query(self, sql): pass
