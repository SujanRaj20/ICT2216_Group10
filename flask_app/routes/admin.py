from flask import Blueprint, render_template

# Create a Blueprint named 'admin'
admin_bp = Blueprint('admin', __name__)

# Define the route for the user profile page
# @admin_bp.route("/admin/<userid>")
# def admin_dashboard(userid):
#     return render_template("admin_dashboard.html", userid=userid)  # Render profile.html with the userid

@admin_bp.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")  # Render the admin dashboard template

@admin_bp.route("/add_admin")
def add_admin():
    return render_template("add_admin.html")  # Render the add admin template

@admin_bp.route("/admin_buyersmenu")
def admin_buyersmenu():
    return render_template("admin_buyersmenu.html")  # Render the add admin template

@admin_bp.route("/admin_sellersmenu")
def admin_sellersmenu():
    return render_template("admin_sellersmenu.html")  # Render the add admin template

@admin_bp.route("/admin_listingsmenu")
def admin_listingsmenu():
    return render_template("admin_listingsmenu.html")  # Render the add admin template

@admin_bp.route("/admin_commentsmenu")
def admin_commentsmenu():
    return render_template("admin_commentsmenu.html")  # Render the add admin template

@admin_bp.route("/admin_reportsmenu")
def admin_reportsmenu():
    return render_template("admin_reportsmenu.html")  # Render the add admin template

@admin_bp.route("/admin_logs")
def admin_logsview():
    return render_template("admin_logsview.html")  # Render the add admin template