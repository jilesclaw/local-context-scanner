def authenticate(username, password):
    # Dummy auth logic
    if username == "admin":
        return True
    return False

def generate_token(user):
    # Imagine JWT logic here
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
