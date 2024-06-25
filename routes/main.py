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
    return render_template("contact.html")  # Render the /contact template

@main_bp.route("/shop")
def shop():
    return render_template("shop.html")  # Render the /shop template

@main_bp.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")  # Render the /wishlist template

@main_bp.route("/cart")
def cart():
    return render_template("cart.html")  # Render the /cart template

@main_bp.route("/checkout")
def checkout():
    return render_template("checkout.html")  # Render the /checkout template

@main_bp.route("/buyer-account")
def buyeraccount():
    return render_template("buyer-account.html")  # Render the /buyer-account template

@main_bp.route("/login")
def login():
    return render_template("login.html")  # Render the /login template

@main_bp.route("/signup")
def signup():
    return render_template("signup.html")  # Render the /signup template

@main_bp.route("/seller-login")
def seller_login():
    return render_template("login-seller.html")  # Render the /seller-login template

@main_bp.route("/seller-signup")
def seller_signup():
    return render_template("signup-seller.html")  # Render the /seller-signup template


# Define the route to serve images from the static/img directory for testing purposes 
# REMOVE THIS BEFORE PRODUCTION
@main_bp.route('/img/<filename>')
def send_image(filename):
    return send_from_directory('static/img', filename)  # Send the requested image file