
from functools import wraps

def retry(max_attempts):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    continue
            raise Exception("Max retries")
        return wrapper
    return decorator

@retry(3)
def fetch():
    pass
