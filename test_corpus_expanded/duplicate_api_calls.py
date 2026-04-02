"""duplicate_api_calls.py - Code duplication patterns."""

def validate_user(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    if not data.get("email"):
        raise ValueError("Email required")
    return True

def validate_product(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    if not data.get("price"):
        raise ValueError("Price required")
    return True

def validate_order(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("user_id"):
        raise ValueError("User ID required")
    if not data.get("items"):
        raise ValueError("Items required")
    return True
