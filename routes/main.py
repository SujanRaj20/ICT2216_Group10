from flask import Blueprint, render_template, send_from_directory

# Create a Blueprint named 'main'
main_bp = Blueprint('main', __name__)

# Define the route for the home page
@main_bp.route("/")
def index():
    return render_template("index.html")  # Render the / template

# Add more routes here
@main_bp.route("/contact")
def contact():
    return render_template("contact.html")  # Render the contact.html template

@main_bp.route("/shop")
def shop():
    return render_template("/shop")  # Render the /shop template


# Define the route to serve images from the static/img directory for testing purposes 
# REMOVE THIS BEFORE PRODUCTION
@main_bp.route('/img/<filename>')
def send_image(filename):
    return send_from_directory('static/img', filename)  # Send the requested image file