from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect,flash,current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import stripe
from SqlAlchemy.createTable import User, get_buyers_foradmin, admin_buyerdelete, get_sellers_foradmin, admin_sellerdelete
import json
import os
from werkzeug.utils import secure_filename
import logging
import random
import string

from bcrypt import hashpw, gensalt, checkpw
import bcrypt  # Import bcrypt module directly
import mysql.connector
from db_connector import get_mysql_connection
from flask import send_file
from captcha.image import ImageCaptcha
import io

# Create a Blueprint named 'admin'
admin_bp = Blueprint('admin', __name__)

# Define the route for the user profile page
# @admin_bp.route("/admin/<userid>")
# def admin_dashboard(userid):
#     return render_template("admin_dashboard.html", userid=userid)  # Render profile.html with the userid

@admin_bp.route("/add_admin")
def add_admin_route():
    return render_template("admin-addaccount.html")  # Render the add admin template

@admin_bp.route("/add-admin-account", methods=["POST"])
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
        if not (fname and lname and email and username and password):
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
@login_required
def admin_buyersmenu_route():
    buyers = get_buyers_foradmin()
    return render_template("admin-buyersmenu.html", buyers=buyers)  # Render the add admin template

@admin_bp.route('/admin/buyeraccountdelete/<int:buyer_id>', methods=['POST'])
@login_required
def admin_buyerdelete_route(buyer_id):
    result = admin_buyerdelete(buyer_id)
    if result['success']:
        return jsonify({'message': 'Buyer account deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_sellersmenu")
def admin_sellersmenu_route():
    sellers = get_sellers_foradmin()
    return render_template("admin-sellersmenu.html", sellers=sellers)  # Render the add admin template

@admin_bp.route('/admin/selleraccountdelete/<int:seller_id>', methods=['POST'])
@login_required
def admin_sellerdelete_route(seller_id):
    result = admin_sellerdelete(seller_id)
    if result['success']:
        return jsonify({'message': 'Seller account deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

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