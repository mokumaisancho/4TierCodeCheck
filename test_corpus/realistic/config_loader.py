
import json
import os

def load_config(path=None):
    if path is None:
        path = os.getenv('CONFIG_PATH', 'config.json')
    
    with open(path) as f:
        return json.load(f)

def merge_configs(base, override):
    result = base.copy()
    result.update(override)
    return result
