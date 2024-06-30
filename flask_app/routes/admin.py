from flask import Blueprint, render_template

# Create a Blueprint named 'admin'
admin_bp = Blueprint('admin', __name__)

# Define the route for the user profile page
# @admin_bp.route("/admin/<userid>")
# def admin_dashboard(userid):
#     return render_template("admin_dashboard.html", userid=userid)  # Render profile.html with the userid

@admin_bp.route("/add_admin")
def add_admin_route():
    return render_template("add-admin.html")  # Render the add admin template

@admin_bp.route("/admin_buyersmenu")
def admin_buyersmenu_route():
    return render_template("admin-buyersmenu.html")  # Render the add admin template

@admin_bp.route("/admin_sellersmenu")
def admin_sellersmenu_route():
    return render_template("admin-sellersmenu.html")  # Render the add admin template

@admin_bp.route("/admin_listingsmenu")
def admin_listingsmenu_route():
    return render_template("admin-listingsmenu.html")  # Render the add admin template

@admin_bp.route("/admin_commentsmenu")
def admin_commentsmenu_route():
    return render_template("admin-commentsmenu.html")  # Render the add admin template

@admin_bp.route("/admin_reportsmenu")
def admin_reportsmenu_route():
    return render_template("admin-reportsmenu.html")  # Render the add admin template

@admin_bp.route("/admin_logs")
def admin_logsview_route():
    return render_template("admin-logsview.html")  # Render the add admin template