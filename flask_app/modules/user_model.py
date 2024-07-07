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


class User(UserMixin):  # creat class User that inherits from UserMixin
    def __init__(self, user_data):                      # create __init__ method that takes in user_data
        self.id = user_data['id']                       # set self.id to user_data['id']
        self.username = user_data['username']           # set self.username to user_data['username']
        self.password_hash = user_data['password_hash'] # set self.password_hash to user_data['password_hash']
        self.fname = user_data['fname']                 # set self.fname to user_data['fname']
        self.lname = user_data['lname']                 # set self.lname to user_data['lname']
        self.email = user_data['email']                 # set self.email to user_data['email']
        self.phone_num = user_data['phone_num']         # set self.phone_num to user_data['phone_num']
        self.role = user_data['role']                   # set self.role to user_data['role']
        
    def get_role(self):     # get_role method
        return self.role    # return self.role

    @staticmethod
    def get(user_id):                                       # get method that takes in user_id
        engine = get_engine()                               # get engine using get_engine function imported from db_engine.py
        user_data = User.get_user_by_id(engine, user_id)    # set user_data to the result of get_user_by_id method
        engine.dispose()
        if user_data:                                       # if user_data is not None
            return User(user_data)                          # return a new instance of User with user_data
        return None
    
    @staticmethod
    def get_user_by_id(engine, user_id):                    # get_user_by_id method that takes in engine and user_id
        query = f"SELECT * FROM users WHERE id = {user_id}" # set query to select all from users where id is equal to user_id
        engine = get_engine()                           
        result = engine.execute(query).fetchone()           # set result to the result of executing the query
        if result:                                          # if result is not None
            return result                                   # return result
        return None
    