from flask import Blueprint, current_app, render_template, send_from_directory, request, redirect, url_for

from flask_login import current_user, login_required

from modules.seller_mods import Listing_Modules
from modules.user_model import User
from modules.buyer_mods import Buyer_Shop, Buyer_Cart, fetch_top_five_bestsellers

from modules.decorators import anonymous_required, buyer_required

from logging_config import configure_logging

# Create a Blueprint named 'main'
main_bp = Blueprint('main', __name__)

def rolechecker():
    if current_user.is_authenticated:
        user_role = current_user.get_role()
    else:
        user_role = 'Guest'
    
    return user_role

# Define the route for the home page
# @main_bp.route("/")
# def index():
#     user_role = rolechecker()
#     return render_template("util-templates/index.html", user_role=user_role)  # Render the / 

@main_bp.route("/")
def index():
    try:
        user_role = rolechecker()
        top_listings = fetch_top_five_bestsellers()
        return render_template("util-templates/index.html", user_role=user_role, top_listings=top_listings)
    except Exception as e:
        current_app.logger.error(f"Exception on / [GET]: {e}")
        return "Internal Server Error", 500
    
@main_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template("util-templates/login.html")  # Render the /login template

@main_bp.route("/signup")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template("buyer-templates/buyer-signup.html")  # Render the /signup template

# Add more routes here
@main_bp.route("/contact")
def contact():
    return render_template("util-templates/contact.html")  # Render the /contact template

@main_bp.route("/shop")
def shop():
    sort_option = request.args.get('sort', 'none')
    category = request.args.get('category', 'all')
    listings = Buyer_Shop.fetch_all_listings_forbuyer(sort_option, category)
    category_counts = Buyer_Shop.fetch_category_counts_for_shop_buyer()
    return render_template("buyer-templates/buyer-shop.html", listings=listings, sort_option=sort_option, category=category, category_counts=category_counts)  # Render the /shop template

@main_bp.route("/checkout")
@buyer_required()
@login_required
def checkout():
    return render_template("buyer-templates/buyer-checkout.html")  # Render the /checkout template

@main_bp.route("/buyer-account")
@buyer_required()
@login_required
def buyeraccount():
    return render_template("buyer-templates/buyer-account.html")  # Render the /buyer-account template

# @main_bp.route("/seller-login")
# def seller_login():
#     return render_template("login-seller.html")  # Render the /seller-login template

@main_bp.route("/seller-signup")
def seller_signup():
    return render_template("seller-templates/seller-signup.html")  # Render the /seller-signup template

# Define the route to serve images from the static/img directory for testing purposes 
# REMOVE THIS BEFORE PRODUCTION
# @main_bp.route('/img/<filename>')
# def send_image(filename):
#     return send_from_directory('static/img', filename)  # Send the requested image file