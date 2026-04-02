
from datetime import datetime

class BaseModel:
    def __init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def save(self):
        self.updated_at = datetime.now()
        # TODO: implement actual save
        pass

class User(BaseModel):
    def __init__(self, name, email):
        super().__init__()
        self.name = name
        self.email = email
