from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask import Flask

# Initialize Flask app
app = Flask(__name__, static_url_path='/static')

# Configure SQLAlchemy
# Replace 'mysql+mysqlconnector' with your MySQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:***REMOVED***@172.17.0.2:3306/***REMOVED***'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

def init_db():
    try:
        # Test the database connection
        with db.engine.connect() as connection:
            query = text('SELECT 1')
            result = connection.execute(query)
            print(f"Database connection successful: {result.fetchone()}")
    except Exception as e:
        print(f"Error connecting to database: {e}")