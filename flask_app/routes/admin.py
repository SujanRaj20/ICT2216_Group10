from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for
from flask_login import login_required, current_user
from modules.admin_mods import (
    get_buyers_foradmin, admin_buyerdelete, get_sellers_foradmin, admin_sellerdelete,
    get_listings_foradmin, admin_listingdelete, get_comments_foradmin, admin_commentdelete,
    get_commentreports_foradmin, get_listingreports_foradmin, admin_commentreportdelete, admin_listingreportdelete
)
import logging
from bcrypt import hashpw, gensalt
import mysql.connector
from modules.db_connector import get_mysql_connection
from modules.decorators import admin_required

# Create a Blueprint named 'admin'
admin_bp = Blueprint('admin', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

# Define the route for adding an admin
@admin_bp.route("/add_admin")
@admin_required()
@login_required
def add_admin_route():
    return render_template("admin-templates/admin-addaccount.html")  # Render the add admin template

@admin_bp.route("/add-admin-account", methods=["POST"])
@admin_required()
@login_required
def add_admin_account():
    try:
        data = request.get_json()
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        phone_num = data.get('phone_num')
        username = data.get('username')
        password = data.get('password')
        role = 'admin'
        captcha_input = data.get('captcha')
        
        # Validate CAPTCHA
        if captcha_input != session.get('captcha_text'):
            return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400
        
        # Basic server-side validation
        if not (fname, lname, email, username, password):
            return jsonify({'error': 'All fields except phone number are required'}), 400
        
        # Hash the password before saving
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if email, username, or phone number already exists
            query = """
            SELECT * FROM users WHERE email = %s OR username = %s OR phone_num = %s
            """
            cursor.execute(query, (email, username, phone_num))
            existing_users = cursor.fetchall()
            
            if existing_users:
                existing_fields = []
                for user in existing_users:
                    if user[5] == email:
                        existing_fields.append("Email")
                    if user[1] == username:
                        existing_fields.append("Username")
                    if user[6] == phone_num:
                        existing_fields.append("Phone Number")
                
                return jsonify({'error': f'The following fields already exist: {", ".join(existing_fields)}'}), 400
            
            # Insert user into the database
            insert_query = """
            INSERT INTO users (fname, lname, email, phone_num, username, password_hash, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (fname, lname, email, phone_num, username, hashed_password.decode('utf-8'), role))
            conn.commit()
            conn.close()
            return jsonify({'message': 'User signed up successfully'})
        else:
            return jsonify({'error': 'Failed to connect to database'}), 500
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route("/admin_buyersmenu")
@admin_required()
@login_required
def admin_buyersmenu_route():
    buyers = get_buyers_foradmin()
    return render_template("admin-templates/admin-buyersmenu.html", buyers=buyers)  # Render the buyers menu template

@admin_bp.route('/admin/buyeraccountdelete/<int:buyer_id>', methods=['POST'])
@admin_required()
@login_required
def admin_buyerdelete_route(buyer_id):
    result = admin_buyerdelete(buyer_id)
    if result['success']:
        return jsonify({'message': 'Buyer account deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_sellersmenu")
@admin_required()
@login_required
def admin_sellersmenu_route():
    sellers = get_sellers_foradmin()
    return render_template("admin-templates/admin-sellersmenu.html", sellers=sellers)  # Render the sellers menu template

@admin_bp.route('/admin/selleraccountdelete/<int:seller_id>', methods=['POST'])
@admin_required()
@login_required
def admin_sellerdelete_route(seller_id):
    result = admin_sellerdelete(seller_id)
    if result['success']:
        return jsonify({'message': 'Seller account deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_listingsmenu")
@admin_required()
@login_required
def admin_listingsmenu_route():
    listings = get_listings_foradmin()
    return render_template("admin-templates/admin-listingsmenu.html", listings=listings)  # Render the listings menu template

@admin_bp.route('/admin/listingdelete/<int:listing_id>', methods=['POST'])
@admin_required()
@login_required
def admin_listingdelete_route(listing_id):
    result = admin_listingdelete(listing_id)
    if result['success']:
        return jsonify({'message': 'Listing deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_commentsmenu")
@admin_required()
@login_required
def admin_commentsmenu_route():
    comments = get_comments_foradmin()
    return render_template("admin-templates/admin-commentsmenu.html", comments=comments)  # Render the comments menu template

@admin_bp.route('/admin/commentdelete/<int:comment_id>', methods=['POST'])
@admin_required()
@login_required
def admin_commentdelete_route(comment_id):
    current_app.logger.debug(f"delete comment id: {comment_id}")
    result = admin_commentdelete(comment_id)
    if result['success']:
        return jsonify({'message': 'Comment deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_reportsmenu")
@admin_required()
@login_required
def admin_reportsmenu_route():
    listing_reports = get_listingreports_foradmin()
    comment_reports = get_commentreports_foradmin()
    current_app.logger.debug(comment_reports)
    current_app.logger.debug(listing_reports)
    return render_template("admin-templates/admin-reportsmenu.html", listing_reports=listing_reports, comment_reports=comment_reports)  # Render the reports menu template

@admin_bp.route('/admin/commentreportdelete/<int:report_id>', methods=['POST'])
@admin_required()
@login_required
def admin_commentreportdelete_route(report_id):
    current_app.logger.debug(f"delete comment report id: {report_id}")
    result = admin_commentreportdelete(report_id)
    if result['success']:
        return jsonify({'message': 'Report deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@admin_bp.route('/admin/listingreportdelete/<int:report_id>', methods=['POST'])
@admin_required()
@login_required
def admin_listingreportdelete_route(report_id):
    current_app.logger.debug(f"delete listing report id: {report_id}")
    result = admin_listingreportdelete(report_id)
    if result['success']:
        return jsonify({'message': 'Report deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_logs")
@admin_required()
@login_required
def admin_logsview_route():
    return render_template("admin-templates/admin-logsview.html")  # Render the logs view template
