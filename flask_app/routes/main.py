from flask import Blueprint, current_app, render_template, send_from_directory, request, redirect, url_for

from flask_login import current_user, login_required

from modules.seller_mods import Listing_Modules
from modules.user_model import User
from modules.buyer_mods import Buyer_Shop, Buyer_Cart, fetch_top_five_bestsellers

from modules.decorators import anonymous_required, buyer_required, non_admin_required

# Create a Blueprint named 'main'
main_bp = Blueprint('main', __name__)

def rolechecker():                              # rolechecker function to check the role of the user
    if current_user.is_authenticated:           # If the user is authenticated then 
        user_role = current_user.get_role()     # grab the value for user's role using get_role() method
    else:                                       # Otherwise
        user_role = 'Guest'                     # set the user_role to 'Guest'
    
    return user_role                            # Return the user_role


@main_bp.route("/")     # Define the route for the index page
def index():
    try:
        user_role = rolechecker()   # Call the rolechecker function to check the role of the user
        top_listings = fetch_top_five_bestsellers() # Fetch the top five bestsellers from the database
        return render_template("util-templates/index.html", user_role=user_role, top_listings=top_listings) # Render the /index template with the user_role and top_listings
    except Exception as e:
        current_app.logger.error(f"Exception on / [GET]: {e}")  # Log the exception
        return "Internal Server Error", 500 # Return a 500 Internal Server Error response
    
@main_bp.route("/login")    # Define the route for the login page
def login():
    if current_user.is_authenticated:   # If the user is authenticated then
        return redirect(url_for('main.index'))  # Redirect the user to the index page
    return render_template("util-templates/login.html")  # Render the /login template if the user is not authenticated

@main_bp.route("/signup")   # Define the route for the signup page
@non_admin_required()
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template("buyer-templates/buyer-signup.html")  # Render the /signup template

# @main_bp.route("/contact")  # Define the route for the contact page
# def contact():
#     return render_template("util-templates/contact.html")  # Render the /contact template

@main_bp.route("/contact")  # Define the route for the contact page
def contact():
    try:
        user_role = rolechecker()   # Call the rolechecker function to check the role of the user
        return render_template("util-templates/contact.html", user_role=user_role)  # Render the /contact template with the user_role
    except Exception as e:
        current_app.logger.error(f"Exception on /contact [GET]: {e}")  # Log the exception
        return "Internal Server Error", 500  # Return a 500 Internal Server Error response

@main_bp.route("/shop")    # Define the route for the shop page
@non_admin_required()      # Use the custom non_admin_required decorator to ensure that only admins cant access the shop page      
def shop():
    sort_option = request.args.get('sort', 'none')                              # Get the sort option from the query string
    category = request.args.get('category', 'all')                              # Get the category from the query string
    listings = Buyer_Shop.fetch_all_listings_forbuyer(sort_option, category)    # Fetch all listings for the buyer using the fetch_all_listings_forbuyer method from the Buyer_Shop class, passing the sort_option and category
    category_counts = Buyer_Shop.fetch_category_counts_for_shop_buyer()         # Fetch the category counts for the shop buyer using the fetch_category_counts_for_shop_buyer method from the Buyer_Shop class
    return render_template("buyer-templates/buyer-shop.html", listings=listings, sort_option=sort_option, category=category, category_counts=category_counts)  # Render the /shop template

@main_bp.route("/checkout") # Define the route for the checkout page
@buyer_required()           # Use the custom buyer_required decorator to ensure that only buyers can access the checkout page
@login_required
def checkout():
    return render_template("buyer-templates/buyer-checkout.html")  # Render the /checkout template

@main_bp.route("/buyer-account")    # Define the route for the buyer account page
@buyer_required()
@login_required
def buyeraccount():
    return render_template("buyer-templates/buyer-account.html")  # Render the /buyer-account template


@main_bp.route("/seller-signup")    # Define the route for the seller signup page
@non_admin_required()
def seller_signup():
    return render_template("seller-templates/seller-signup.html")  # Render the /seller-signup template
