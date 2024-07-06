from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for, send_file  
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

from modules.logger import get_dates_with_logs, get_logs_within_date_range

import os

from io import BytesIO
import zipfile

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
            
            current_app.logger.info(f"Admin {current_user.id} added another admin account {email}")
            return jsonify({'message': 'User signed up successfully'})
        else:
            current_app.logger.error(f"Error in add_admin_account connecting to database")
            return jsonify({'error': 'Failed to connect to database'}), 500
    except mysql.connector.Error as err:
        current_app.logger.error(f"Database error for add admin account: {err}")
        return jsonify({'error': f"Database error for add admin account: {err}"}), 500
    except Exception as e:
        current_app.logger.error(f"Error for add admin account: {str(e)}")
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
        current_app.logger.info(f"Admin {current_user.id} deleted buyer {buyer_id}")
        return jsonify({'message': 'Buyer account deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in admin_buyersmenu_route")
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
        current_app.logger.info(f"Admin {current_user.id} deleted seller {seller_id}")
        return jsonify({'message': 'Seller account deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in admin_sellerdelete_route")
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
        current_app.logger.info(f"Admin {current_user.id} deleted listing {listing_id}")
        return jsonify({'message': 'Listing deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in admin_listingdelete_route")
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
        current_app.logger.info(f"Admin {current_user.id} deleted comment {comment_id}")
        return jsonify({'message': 'Comment deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in admin_commentdelete_route")
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_reportsmenu")
@admin_required()
@login_required
def admin_reportsmenu_route():
    listing_reports = get_listingreports_foradmin()
    comment_reports = get_commentreports_foradmin()
    # current_app.logger.debug(comment_reports)
    # current_app.logger.debug(listing_reports)
    return render_template("admin-templates/admin-reportsmenu.html", listing_reports=listing_reports, comment_reports=comment_reports)  # Render the reports menu template

@admin_bp.route('/admin/commentreportdelete/<int:report_id>', methods=['POST'])
@admin_required()
@login_required
def admin_commentreportdelete_route(report_id):
    current_app.logger.debug(f"delete comment report id: {report_id}")
    result = admin_commentreportdelete(report_id)
    if result['success']:
        current_app.logger.info(f"Admin {current_user.id} deleted comment report {report_id}")
        return jsonify({'message': 'Report deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in admin_commentreportdelete_route")
        return jsonify({'error': result['error']}), 400

@admin_bp.route('/admin/listingreportdelete/<int:report_id>', methods=['POST'])
@admin_required()
@login_required
def admin_listingreportdelete_route(report_id):
    current_app.logger.debug(f"delete listing report id: {report_id}")
    result = admin_listingreportdelete(report_id)
    if result['success']:
        current_app.logger.info(f"Admin {current_user.id} deleted listing report {report_id}")
        return jsonify({'message': 'Report deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in admin_listingreportdelete_route")
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_logs")
@admin_required()
@login_required
def admin_logsview_route():
    dates = get_dates_with_logs()
    current_app.logger.info(f"Admin {current_user.id} accessed logs page")
    return render_template("admin-templates/admin-logsview.html", dates=dates)  # Render the logs view template

@admin_bp.route("/admin_download_logs", methods=['POST'])
@admin_required()
@login_required
def admin_download_logs():
    try:
        data = request.get_json()
        start_date = data['start_date']
        end_date = data['end_date']
        
        # Validate dates to ensure end_date is not before start_date
        if start_date > end_date:
            return jsonify({'error': 'End date cannot be before start date.'}), 400
        
        current_app.logger.info(f"Admin {current_user.id} downloading logs from {start_date} to {end_date}")
        
        log_files = get_logs_within_date_range(start_date, end_date)

        # Create a zip file of the selected log files
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for log_file in log_files:
                log_path = os.path.join('logs', log_file)
                zip_file.write(log_path, os.path.basename(log_path))

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'logs_{start_date}_to_{end_date}.zip'
        )

    except KeyError as e:
        error_message = f'Missing or invalid key in request JSON: {e}'
        current_app.logger.error(error_message)
        return jsonify({'error': error_message}), 400

    except Exception as e:
        error_message = f'Error downloading logs: {e}'
        current_app.logger.error(error_message)
        return jsonify({'error': error_message}), 500