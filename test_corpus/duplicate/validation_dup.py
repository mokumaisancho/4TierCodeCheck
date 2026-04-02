
def validate_user(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    return True

def validate_product(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    return True
