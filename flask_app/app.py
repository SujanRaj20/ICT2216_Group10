from dotenv import load_dotenv
from flask import Flask, render_template, g, redirect, url_for, session, request, jsonify, current_app # Import dependencies  from flask
from flask_login import LoginManager, login_user, logout_user, login_required, current_user # Import dependancies from flask-login 
import os 
from jinja2 import TemplateNotFound  # Import the TemplateNotFound exception
from datetime import timedelta # Import timedelta from datetime to measure time difference

import stripe # Import the stripe package for checkout

from routes.main import main_bp  # Import the main Blueprint file from the routes module
from routes.user import user_bp  # Import the user Blueprint 
from routes.admin import admin_bp  # Import the admin Blueprint

from SqlAlchemy.createTable import create_or_verify_tables, print_tables_or_fields_created # Import required modules form the createTable file 
from modules.user_model import User # Import the custom Users model
from modules.buyer_mods import Buyer_Cart # Import Buyer_Cart class from the buyer_mods file
from modules.db_engine import get_engine # Import get_engine function from the get_engine file
from modules.db_connector import get_mysql_connection # Import the get_mysql_connection function from the db_connector file
from modules.decorators import anonymous_required # Import the required decorators from the decorators file
from modules.logger import configure_logging # Import the configure_logging function from the logger file

from flask_mail import Mail # Import the Mail package from flask-mail (for OTP)

import mysql.connector


# Configure logging
configure_logging()

# Load environment variables from .env file
load_dotenv()

# Helper function to convert strings to booleans
def str_to_bool(value):
    return value.lower() in ('true', '1', 't', 'y', 'yes')

# Initialize the Flask application
app = Flask(__name__, static_url_path='/static')


app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reloading of templates
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1) # Set the maximum lifetime duration of a permanent session to 1 hour
app.secret_key = os.urandom(24)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = str_to_bool(os.getenv('MAIL_USE_TLS'))
app.config['MAIL_USE_SSL'] = str_to_bool(os.getenv('MAIL_USE_SSL'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')

app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Configure the app with environment variables
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')

# Set the Stripe API key
stripe.api_key = app.config['STRIPE_SECRET_KEY']

app.logger.info('Initiated app')

app.logger.info('Initializing mail')
mail = Mail(app) # Initialize Mail

# Define the custom filter for enumerate
def jinja2_enumerate(sequence, start=0):
    return enumerate(sequence, start=start)

# Register the filter
app.jinja_env.filters['enumerate'] = jinja2_enumerate

# Function to get the user's cart item count to display on all pages in the navbar if they're logged in
@app.context_processor
def inject_user_cart_count():
    if current_user.is_authenticated:                                               # If the user is authenticated then grab the value for user's cart item count using 
        user_cart_count = Buyer_Cart.get_user_cart_item_count(current_user.id)      # the get_user_cart_item_count funtion from the imported Buyer_Cart class
    else:
        user_cart_count = '0'
    return dict(user_cart_count=user_cart_count)


app.logger.info('Initializing LoginManager')    
login_manager = LoginManager()  # Set-up login manager 
login_manager.init_app(app)     # Initialize the login-manager for this app

app.logger.info('Registering Blueprints')
# Register the Blueprint with the app
app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)



app.logger.info('Initializing Database')
def initialize_database():
    """Function to initialize the database and create/verify tables."""
    print("Initializing database...")
    try:
        local_engine = get_engine() # Create and receive engine from the get_engine function imported earlier
        print("Engine created.")
        
        tables_or_fields = create_or_verify_tables(local_engine) # Fetch tables that were created or verified to have already existed 
        print_tables_or_fields_created(tables_or_fields) # print the results
        
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
def load_user(user_id):         #load the current user
    return User.get(user_id)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    db = get_mysql_connection()  # Use the existing get_mysql_connection function
    cursor = db.cursor(dictionary=True) 
    search_query = """
    SELECT * FROM listings                                                              
    WHERE title LIKE %s OR description LIKE %s OR keywords LIKE %s OR author LIKE %s    
    """                                                                                 # this query is used to take input from the search box and compares 
    like_query = f"%{query}%"                                                           # it to the description and keywords fields for each listing
    cursor.execute(search_query, (like_query, like_query, like_query, like_query))  
    results = cursor.fetchall()                                                         # listings with matches to the search term are fetched
    cursor.close()
    db.close()
    return jsonify(results)                                                             # returns the listings/results to show to the user 

# Initialize the database tables when the app starts
with app.app_context():
    initialize_database()
        
# Run the app in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('util-templates/404.html'), 404 # Display the 404 page whenever a non-existant route is called

# # Error handler for TemplateNotFound errors
@app.errorhandler(TemplateNotFound)
def template_not_found(e):
    return render_template('util-templates/404.html'), 404