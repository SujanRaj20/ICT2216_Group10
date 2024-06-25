from flask import Blueprint, render_template

# Create a Blueprint named 'sellerpage'
sellerpage_bp = Blueprint('sellerpage', __name__)

# Define the route for the user profile page
@user_bp.route("/seller/<sellerid>")
def profile(sellerid):
    return render_template("seller.html", sellerid=sellerid)  # Render seller.html with the sellerid