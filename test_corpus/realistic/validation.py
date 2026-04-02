
import re

def validate_username(username):
    if not username:
        return False, "Username required"
    if len(username) < 3:
        return False, "Too short"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Invalid characters"
    return True, None

def validate_password(password):
    if len(password) < 8:
        return False, "Too short"
    if not any(c.isupper() for c in password):
        return False, "Need uppercase"
    if not any(c.isdigit() for c in password):
        return False, "Need digit"
    return True, None
