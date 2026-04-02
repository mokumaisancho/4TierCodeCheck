
import json

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        return {"status": 200, "url": url}
    
    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        return {"status": 201, "data": data}
