from flask_login import UserMixin
from dbmodules.db_engine import get_engine

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']
        self.fname = user_data['fname']
        self.lname = user_data['lname']
        self.email = user_data['email']
        self.phone_num = user_data['phone_num']
        self.role = user_data['role']
        
    def get_role(self):
        return self.role

    @staticmethod
    def get(user_id):
        engine = get_engine()
        user_data = get_user_by_id(engine, user_id)
        engine.dispose()
        if user_data:
            return User(user_data)
        return None
    