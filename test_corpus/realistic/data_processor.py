
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = {}
    
    def process(self, data):
        if data['id'] in self.cache:
            return self.cache[data['id']]
        result = self.transform(data)
        self.cache[data['id']] = result
        return result
    
    def transform(self, data):
        return {k: v.upper() if isinstance(v, str) else v 
                for k, v in data.items()}
