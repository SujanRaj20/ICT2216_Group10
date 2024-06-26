from flask import Flask, render_template,g
import os
from jinja2 import TemplateNotFound  # Import the TemplateNotFound exception
from routes.main import main_bp  # Import the Blueprint from the routes module
from routes.user import user_bp  # Import the user Blueprint
from routes.admin import admin_bp  # Import the admin Blueprint

from db_connector import get_mysql_connection
# from sqlalchemy import text
import mysql.connector

# Initialize the Flask application
app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reloading of templates
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:***REMOVED***@172.18.0.2/***REMOVED***'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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

# Run the app in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
