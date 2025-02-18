from flask_login import LoginManager, UserMixin, login_user




class User(UserMixin):
    def __init__(self, user_id, username, password,role,status):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.is_active = status

    def get_id(self):
        return self.user_id
    def is_active(self):
        return self._is_active
    


