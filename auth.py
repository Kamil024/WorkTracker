import db

#  AUTHENTICATION 

def authenticate_user(username, password):
    """Authenticate a user by verifying credentials."""
    return db.authenticate_user(username, password)


def register_user(username, password):
    """Register a new user if username not taken."""
    return db.register_user(username, password)


#  SESSION MANAGEMENT 

def save_login_state(user_data):
    """Save current logged-in user's info (id, username)."""
    if user_data:
        db.save_login_state(user_data)


def load_login_state():
    """Load saved login session."""
    return db.load_login_state()


def logout():
    """Log out current user and clear saved session."""
    try:
        db.clear_login_state()
        return True
    except Exception as e:
        print(f"[AUTH] logout error: {e}")
        return False
