import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

# Load environment variables from .env file
load_dotenv()

# MySQL Server Parameters - Local
local_mysql_host = os.getenv('MYSQL_HOST')
local_mysql_port = os.getenv('MYSQL_PORT')
local_mysql_user = os.getenv('MYSQL_USER')
local_mysql_password = os.getenv('MYSQL_PASSWORD')
local_mysql_db = os.getenv('MYSQL_DB')

def get_engine():   # Function to return a MySQL engine when called
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    return engine