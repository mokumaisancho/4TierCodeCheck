"""mixed_realistic_1.py - Realistic mixed complexity module."""

import json
from pathlib import Path

class DataManager:
    def __init__(self, config):
        self.config = config
        self.cache = {}
    
    def load(self, filepath):
        path = Path(filepath)
        if not path.exists():
            return None
        
        if filepath in self.cache:
            return self.cache[filepath]
        
        with open(filepath) as f:
            data = json.load(f)
        
        processed = self._process(data)
        self.cache[filepath] = processed
        return processed
    
    def _process(self, data):
        if isinstance(data, list):
            return [self._process(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._process(v) for k, v in data.items()}
        return data

def utility_function(items, predicate=None):
    if not items:
        return []
    results = []
    for item in items:
        if predicate is None or predicate(item):
            results.append(item)
    return results
