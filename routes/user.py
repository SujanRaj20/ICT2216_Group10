from flask import Blueprint, render_template

# Create a Blueprint named 'user'
user_bp = Blueprint('user', __name__)

# Define the route for the user profile page
@user_bp.route("/user/<username>")
def profile(userid):
    return render_template("profile.html", userid=userid)  # Render profile.html with the userid