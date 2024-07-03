import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG


# MySQL Server Parameters - Local
local_mysql_host = os.getenv('MYSQL_HOST', 'mysql-container')
local_mysql_port = 3306
local_mysql_user = os.getenv('MYSQL_USER', 'bookwise_flask')
local_mysql_password = os.getenv('MYSQL_PASSWORD', '***REMOVED***')
local_mysql_db = os.getenv('MYSQL_DB', '***REMOVED***')

def get_engine():
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    return engine