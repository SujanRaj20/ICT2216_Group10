from flask import Blueprint, render_template, send_from_directory, request, jsonify, url_for, session, redirect,flash,current_app
from SqlAlchemy.createTable import create_or_verify_tables, print_tables_or_fields_created, User, authenticate_user, get_user_by_id
from SqlAlchemy.createTable import User, fetch_all_listings_forbuyer, get_listing_byid, delete_listing_fromdb, fetch_category_counts_for_shop_buyer, get_user_cart_item_count
from flask_login import current_user

# Create a Blueprint named 'main'
main_bp = Blueprint('main', __name__)

def rolechecker():
    if current_user.is_authenticated:
        user_role = current_user.get_role()
    else:
        user_role = 'Guest'
    
    return user_role

# Define the route for the home page
@main_bp.route("/")
def index():
    user_role = rolechecker()
    return render_template("util-templates/index.html", user_role=user_role)  # Render the / 

# Add more routes here
@main_bp.route("/contact")
def contact():
    return render_template("util-templates/contact.html")  # Render the /contact template

@main_bp.route("/shop")
def shop():
    sort_option = request.args.get('sort', 'none')
    category = request.args.get('category', 'all')
    listings = fetch_all_listings_forbuyer(sort_option, category)
    category_counts = fetch_category_counts_for_shop_buyer()
    return render_template("buyer-templates/shop.html", listings=listings, sort_option=sort_option, category=category, category_counts=category_counts)  # Render the /shop template

@main_bp.route("/checkout")
def checkout():
    return render_template("buyer-templates/buyer-checkout.html")  # Render the /checkout template

@main_bp.route("/buyer-account")
def buyeraccount():
    return render_template("buyer-templates/buyer-account.html")  # Render the /buyer-account template

@main_bp.route("/login")
def login():
    return render_template("util-templates/login.html")  # Render the /login template

@main_bp.route("/signup")
def signup():
    return render_template("buyer-templates/buyer-signup.html")  # Render the /signup template

@main_bp.route("/seller-login")
def seller_login():
    return render_template("login-seller.html")  # Render the /seller-login template

@main_bp.route("/seller-signup")
def seller_signup():
    return render_template("seller-templates/seller-signup.html")  # Render the /seller-signup template


# Define the route to serve images from the static/img directory for testing purposes 
# REMOVE THIS BEFORE PRODUCTION
@main_bp.route('/img/<filename>')
def send_image(filename):
    return send_from_directory('static/img', filename)  # Send the requested image file