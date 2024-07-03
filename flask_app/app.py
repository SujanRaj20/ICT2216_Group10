from flask import Flask, render_template, g, redirect, url_for, session, request, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from jinja2 import TemplateNotFound  # Import the TemplateNotFound exception
from datetime import timedelta

import stripe

from SqlAlchemy.createTable import create_or_verify_tables, print_tables_or_fields_created
from routes.main import main_bp  # Import the Blueprint from the routes module
from routes.user import user_bp  # Import the user Blueprint
from routes.admin import admin_bp  # Import the admin Blueprint
from endpoint_config import protected_endpoints  # Import protected endpoints

from dbmodules.user_model import User
from dbmodules.buyer_mods import Buyer_Cart
from dbmodules.db_connector import get_mysql_connection
from sqlalchemy import create_engine  # Import create_engine from SQLAlchemy
# from sqlalchemy import text
import mysql.connector
import logging
from flask_mail import Mail


# Initialize the Flask application
app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reloading of templates
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.secret_key = os.urandom(24)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = '***REMOVED***'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '***REMOVED***'
app.config['MAIL_PASSWORD'] = '***REMOVED***'  # Use your Gmail App Password here

# Initialize Mail
mail = Mail(app)

# Define the custom filter for enumerate
def jinja2_enumerate(sequence, start=0):
    return enumerate(sequence, start=start)

# Register the filter
app.jinja_env.filters['enumerate'] = jinja2_enumerate

@app.context_processor
def inject_user_cart_count():
    if current_user.is_authenticated:
        user_cart_count = Buyer_Cart.get_user_cart_item_count(current_user.id)
    else:
        user_cart_count = '0'
    return dict(user_cart_count=user_cart_count)

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG for all loggers

# Optionally, configure Flask's logger to use the same settings
app.logger.setLevel(logging.DEBUG)

app.logger.debug("This is a debug message")

login_manager = LoginManager()
login_manager.init_app(app)

local_mysql_host = os.getenv('MYSQL_HOST', 'mysql-container')
local_mysql_port = 3306
local_mysql_user = os.getenv('MYSQL_USER', 'bookwise_flask')
local_mysql_password = os.getenv('MYSQL_PASSWORD', '***REMOVED***')
local_mysql_db = os.getenv('MYSQL_DB', '***REMOVED***')

# Register the Blueprint with the app
app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

# # Error handler for 404 errors
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404 # Display the 404 page whenever a non-existant route is called

# # # Error handler for TemplateNotFound errors
# @app.errorhandler(TemplateNotFound)
# def template_not_found(e):
#     return render_template('404.html'), 404

# Route to create a user (just for example)


def initialize_database():
    """Function to initialize the database and create/verify tables."""
    print("Initializing database...")
    try:
        local_db_uri = f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}'
        local_engine = create_engine(local_db_uri)
        print("Engine created.")
        
        tables_or_fields = create_or_verify_tables(local_engine)
        print_tables_or_fields_created(tables_or_fields)
        
        print("Tables created or verified successfully for local MySQL.")
        print("\nFields in Each Table:")
        for table in local_engine.table_names():
            print(f"Table: {table}")
            for column in local_engine.execute(f"DESCRIBE {table}"):
                print(f" - {column['Field']} ({column['Type']})")
        print("Database initialization completed.")

    except Exception as e:
        print(f"Error creating tables: {e}")

    finally:
        if 'local_engine' in locals():
            local_engine.dispose()
            print("Engine disposed.")
            

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/dbconntest')
def dbconntest():
    try:
        # Test the database connection
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return f"Database connection successful yay: {result}"
        else:
            return "Failed to connect to database"
    except Exception as e:
        return f"Error connecting to database: {e}"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    db = get_mysql_connection()  # Use the existing get_mysql_connection function
    cursor = db.cursor(dictionary=True)
    search_query = """
    SELECT * FROM listings 
    WHERE title LIKE %s OR description LIKE %s OR keywords LIKE %s OR author LIKE %s
    """
    like_query = f"%{query}%"
    cursor.execute(search_query, (like_query, like_query, like_query, like_query))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(results)

# Before request handler to check if user is logged in for specific endpoints
@app.before_request
def before_request():
    if request.endpoint in protected_endpoints and 'user_id' not in session:
        return redirect(url_for('user.login'))  # Redirect to login page if not logged in

# Initialize the database tables when the app starts
with app.app_context():
    initialize_database()
        
# Run the app in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
