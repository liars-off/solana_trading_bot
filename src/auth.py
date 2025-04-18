from flask_login import UserMixin
import os
from dotenv import load_dotenv

load_dotenv()

class User(UserMixin):
    def __init__(self, username):
        self.id = username

def check_credentials(username, password):
    from werkzeug.security import check_password_hash
    if username == os.getenv('ADMIN_USERNAME'):
        return check_password_hash(os.getenv('ADMIN_PASSWORD_HASH'), password)
    return False