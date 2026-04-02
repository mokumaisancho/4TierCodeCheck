
from functools import wraps

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = kwargs.get('auth_token')
        if not auth:
            raise PermissionError("No auth token")
        return func(*args, **kwargs)
    return wrapper

def check_role(user, required_role):
    return user.get('role') == required_role
