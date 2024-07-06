from flask_login import UserMixin
from modules.db_engine import get_engine

import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime
import os


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
        user_data = User.get_user_by_id(engine, user_id)
        engine.dispose()
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_user_by_id(engine, user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        engine = get_engine()
        result = engine.execute(query).fetchone()
        if result:
            return result
        return None
    