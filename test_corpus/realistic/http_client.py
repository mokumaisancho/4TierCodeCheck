
import urllib.request
import json

class HTTPClient:
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url
        self.timeout = timeout
    
    def get(self, path):
        url = f"{self.base_url}{path}"
        with urllib.request.urlopen(url, timeout=self.timeout) as resp:
            return json.loads(resp.read())
    
    def post(self, path, data):
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())
