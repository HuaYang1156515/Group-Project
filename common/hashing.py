from flask_hashing import Hashing
from config import setting


hashing = Hashing()

# Optionally, you can provide a Flask app later when it's available
def init_app(app=None):
    if app:
        hashing.init_app(app)

def hash_value(value):
    return hashing.hash_value(value, setting.salt)

def check_value(value, hashed_value):
    return hashing.check_value(value, hashed_value, setting.salt)
