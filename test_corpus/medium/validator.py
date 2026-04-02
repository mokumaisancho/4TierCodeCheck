
def validate_email(email):
    if '@' not in email:
        return False
    if '.' not in email.split('@')[1]:
        return False
    return True

def validate_phone(phone):
    digits = ''.join(c for c in phone if c.isdigit())
    return len(digits) >= 10
