# Import necessary libraries and modules
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

# Create a Blueprint named 'admin' for grouping all admin routes
admin_bp = Blueprint('admin', __name__)

# Configure logging to debug level for detailed log output
logging.basicConfig(level=logging.DEBUG) 

# Route to render the template for adding an admin account
@admin_bp.route("/add_admin")
@admin_required()   # custom decorator to specify that only admins can access this route
@login_required     # built-in decorator to specify that only logged-in users can access this route
def add_admin_route():
    return render_template("admin-templates/admin-addaccount.html")


# Route to handle the POST request for creating an admin account
@admin_bp.route("/add-admin-account", methods=["POST"])
@admin_required() 
@login_required 
def add_admin_account(): # Function to add an admin account when a POST request is made to the route
    try: 
        data = request.get_json()           # Get the JSON data from the request
        fname = data.get('fname')           # Get the first name from the JSON data
        lname = data.get('lname')           # Get the last name
        email = data.get('email')           # Get the email
        phone_num = data.get('phone_num')   # Get the phone number
        username = data.get('username')     # Get the username
        password = data.get('password')     # Get the password
        role = 'admin'                      # Set the role to 'admin' for the new admin account
        captcha_input = data.get('captcha') # Get the CAPTCHA input
        
        # Validate CAPTCHA
        if captcha_input != session.get('captcha_text'): # Check if the CAPTCHA input matches the session value
            return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400 # Return an error if the CAPTCHA is invalid
        
        # Basic server-side validation
        if not (fname, lname, email, username, password): # Check if all fields are provided
            return jsonify({'error': 'All fields except phone number are required'}), 400 # If not, return an error
        
        hashed_password = hashpw(password.encode('utf-8'), gensalt()) # Hash the password using bcrypt and gensalt
        
        conn = get_mysql_connection()   # Get a connection to the MySQL database
        if conn:                        # Check if the connection was successful
            cursor = conn.cursor()      # Get a cursor to execute queries
            
            # Query to check if the email, username, or phone number already exists
            query = """                                                                 
            SELECT * FROM users WHERE email = %s OR username = %s OR phone_num = %s
            """                                                                         
            cursor.execute(query, (email, username, phone_num)) # Execute the query with the provided email, username, and phone number
            existing_users = cursor.fetchall()                  # Fetch the results of the query
            
            if existing_users:                                  # Check if any existing users were found
                existing_fields = []                            # Initialize a list to store the fields that already exist
                for user in existing_users:                     # Iterate over the existing users
                    if user[5] == email:                        # Check if the email already exists
                        existing_fields.append("Email")         # Add 'Email' to the list of existing fields
                    if user[1] == username:                     # Check if the username already exists
                        existing_fields.append("Username")      # Add 'Username' to the list of existing fields
                    if user[6] == phone_num:                    # Check if the phone number already exists
                        existing_fields.append("Phone Number")  # Add 'Phone Number' to the list of existing fields
                
                return jsonify({'error': f'The following fields already exist: {", ".join(existing_fields)}'}), 400 # Return an error with the existing fields
            
            # Insert user into the database
            insert_query = """
            INSERT INTO users (fname, lname, email, phone_num, username, password_hash, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """                                                 # Query to insert the new user into the database
            cursor.execute(insert_query, (fname, lname, email, phone_num, username, hashed_password.decode('utf-8'), role)) # Execute the query with the provided user data
            conn.commit()   # Commit the transaction to the database
            conn.close()    # Close the connection to the database
            
            current_app.logger.info(f"Admin {current_user.id} added another admin account {email}") # Log the successful addition of an admin account
            return jsonify({'message': 'User signed up successfully'})                              # Return a success message
        else:
            current_app.logger.error(f"Error in add_admin_account connecting to database")          # Log the error if the connection to the database failed
            return jsonify({'error': 'Failed to connect to database'}), 500                         # Return an error if the connection failed
    except mysql.connector.Error as err:
        current_app.logger.error(f"Database error for add admin account: {err}")                    # Log the database error
        return jsonify({'error': f"Database error for add admin account: {err}"}), 500              # Return an error with the database error
    except Exception as e:
        current_app.logger.error(f"Error for add admin account: {str(e)}")                          # Log the general error
        return jsonify({'error': str(e)}), 500                                                      # Return an error with the general error           

@admin_bp.route("/admin_buyersmenu") # Route to render the buyers menu template
@admin_required()
@login_required
def admin_buyersmenu_route():
    buyers = get_buyers_foradmin()
    return render_template("admin-templates/admin-buyersmenu.html", buyers=buyers)

@admin_bp.route('/admin/buyeraccountdelete/<int:buyer_id>', methods=['POST']) # Route to handle the POST request for deleting a buyer account
@admin_required()
@login_required
def admin_buyerdelete_route(buyer_id):
    result = admin_buyerdelete(buyer_id) # Call the admin_buyerdelete function to delete the buyer account
    if result['success']:
        current_app.logger.info(f"Admin {current_user.id} deleted buyer {buyer_id}")    # Log the deletion of the buyer account
        return jsonify({'message': 'Buyer account deleted successfully'}), 200          # Return a success message
    else:
        current_app.logger.error(f"Error in admin_buyersmenu_route")                    # Log the error if the deletion failed
        return jsonify({'error': result['error']}), 400                                 # Return an error with the error message

@admin_bp.route("/admin_sellersmenu")   # Route to render the sellers menu template
@admin_required()
@login_required
def admin_sellersmenu_route():
    sellers = get_sellers_foradmin()    # Get the sellers for the admin
    return render_template("admin-templates/admin-sellersmenu.html", sellers=sellers)   # Render the sellers menu template and pass the sellers data

@admin_bp.route('/admin/selleraccountdelete/<int:seller_id>', methods=['POST']) # Route to handle the POST request for deleting a seller account
@admin_required()
@login_required
def admin_sellerdelete_route(seller_id):    
    result = admin_sellerdelete(seller_id)  # Call the admin_sellerdelete function to delete the seller account
    if result['success']:
        current_app.logger.info(f"Admin {current_user.id} deleted seller {seller_id}")
        return jsonify({'message': 'Seller account deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in admin_sellerdelete_route")
        return jsonify({'error': result['error']}), 400

@admin_bp.route("/admin_listingsmenu")  # Route to render the listings menu template
@admin_required()
@login_required
def admin_listingsmenu_route():
    listings = get_listings_foradmin()  # Get the listings for the admin
    return render_template("admin-templates/admin-listingsmenu.html", listings=listings)  # Render the listings menu template and pass the listings data

@admin_bp.route('/admin/listingdelete/<int:listing_id>', methods=['POST'])  # Route to handle the POST request for deleting a listing
@admin_required()
@login_required
def admin_listingdelete_route(listing_id):      
    result = admin_listingdelete(listing_id)    # Call the admin_listingdelete function to delete the listing
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
    return render_template("admin-templates/admin-commentsmenu.html", comments=comments)  # Render the comments menu template and pass the comments data

@admin_bp.route('/admin/commentdelete/<int:comment_id>', methods=['POST'])  # Route to handle the POST request for deleting a comment
@admin_required()
@login_required
def admin_commentdelete_route(comment_id):
    current_app.logger.debug(f"delete comment id: {comment_id}")                            # Log the deletion of the comment
    result = admin_commentdelete(comment_id)                                                # Call the admin_commentdelete function to delete the comment
    if result['success']:
        current_app.logger.info(f"Admin {current_user.id} deleted comment {comment_id}")    # Log the deletion of the comment
        return jsonify({'message': 'Comment deleted successfully'}), 200                    # Return a success message
    else:
        current_app.logger.error(f"Error in admin_commentdelete_route")                     # Log the error if the deletion failed
        return jsonify({'error': result['error']}), 400                                     

@admin_bp.route("/admin_reportsmenu")   # Route to render the reports menu template
@admin_required()
@login_required
def admin_reportsmenu_route():
    listing_reports = get_listingreports_foradmin() # Get the listing reports for the admin
    comment_reports = get_commentreports_foradmin() # Get the comment reports for the admin

    return render_template("admin-templates/admin-reportsmenu.html", listing_reports=listing_reports, comment_reports=comment_reports)  # Render the reports menu template and pass the listing and comment reports data

@admin_bp.route('/admin/commentreportdelete/<int:report_id>', methods=['POST']) # Route to handle the POST request for deleting a comment report
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

@admin_bp.route('/admin/listingreportdelete/<int:report_id>', methods=['POST']) # Route to handle the POST request for deleting a listing report
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

@admin_bp.route("/admin_logs")  # Route to render the logs page
@admin_required()
@login_required
def admin_logsview_route():
    dates = get_dates_with_logs()   # Get the list of dates that have log files using the get_dates_with_logs function imported from logger.py
    current_app.logger.info(f"Admin {current_user.id} accessed logs page")  # Log the access to the logs page
    return render_template("admin-templates/admin-logsview.html", dates=dates)  # Render the logs view template and pass the dates data

@admin_bp.route("/admin_download_logs", methods=['POST'])   # Route to handle the POST request for downloading logs
@admin_required()
@login_required
def admin_download_logs():
    try:
        data = request.get_json()       # Get the JSON data from the request
        start_date = data['start_date'] # Get the start date from the JSON data        
        end_date = data['end_date']     # Get the end date from the JSON data
        
        # Validate dates to ensure end_date is not before start_date
        if start_date > end_date:
            return jsonify({'error': 'End date cannot be before start date.'}), 400 # Return an error if the end date is before the start date
        
        current_app.logger.info(f"Admin {current_user.id} downloading logs from {start_date} to {end_date}")    # Log the download of logs
        
        log_files = get_logs_within_date_range(start_date, end_date)    # Get the log files within the specified date range using the get_logs_within_date_range function imported from logger.py

        # Create a zip file of the selected log files
        zip_buffer = BytesIO()                                          # Create a BytesIO buffer to store the zip file
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:              # Create a ZipFile object with the BytesIO buffer
            for log_file in log_files:                                  # Iterate over the log files
                log_path = os.path.join('logs', log_file)               # Get the path to the log file
                zip_file.write(log_path, os.path.basename(log_path))    # Write the log file to the zip file

        zip_buffer.seek(0)                                              # Reset the buffer position to the beginning

        return send_file(                                               # Return the zip file as a response using send_file function
            zip_buffer,                                                 # Use the zip buffer as the file to send
            mimetype='application/zip',                                 # Set the mimetype to application/zip
            as_attachment=True,                                         # Set as_attachment to True to force download
            download_name=f'logs_{start_date}_to_{end_date}.zip'        # Set the download name for the zip file
        )

    except KeyError as e:                                               # Handle KeyError if required keys are missing in the JSON data
        error_message = f'Missing or invalid key in request JSON: {e}'  # Create an error message
        current_app.logger.error(error_message)                         # Log the error
        return jsonify({'error': error_message}), 400                   # Return an error response with the error message

    except Exception as e:                                              # Handle any other exceptions
        error_message = f'Error downloading logs: {e}'                  # Create an error message
        current_app.logger.error(error_message)                         # Log the error
        return jsonify({'error': error_message}), 500                   # Return an error response with the error message