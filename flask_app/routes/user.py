import base64
from datetime import datetime, timedelta
import time
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect,flash,current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import stripe


from modules.decorators import anonymous_required, seller_required, buyer_required

from modules.seller_mods import Listing_Modules, get_seller_info
from modules.user_model import User
from modules.db_engine import get_engine
from modules.buyer_mods import Buyer_Cart, Buyer_Wishlist, Buyer_Shop, create_comment, create_comment_report, create_report
import json
import os
from werkzeug.utils import secure_filename
import logging
import random
import string

from bcrypt import hashpw, gensalt, checkpw
import bcrypt  # Import bcrypt module directly
import mysql.connector
from modules.db_connector import get_mysql_connection
from flask import send_file
from captcha.image import ImageCaptcha
import io

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')


# Create a Blueprint named 'user'
user_bp = Blueprint('user', __name__)
mail = Mail()

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

def generate_otp():
    """Generate a random 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send an OTP email to the user."""
    msg = Message('Your OTP Code', sender='***REMOVED***', recipients=[email])
    msg.body = f'Your OTP code is {otp}. Please use this code to complete your login.'
    try:
        mail.send(msg)
        current_app.logger.info(f"OTP email sent to {email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send OTP email to {email}: {e}")
        return False
    
def validate_captcha(captcha_input):
    """Validate CAPTCHA input."""
    return captcha_input == session.get('captcha_text')

def validate_otp(otp):
    """Validate the OTP entered by the user."""
    stored_otp = session.get('otp')
    otp_timestamp = session.get('otp_timestamp')
    
    if stored_otp and otp_timestamp:
        return otp == stored_otp and time.time() - otp_timestamp <= 120  # 120 seconds (2 minutes)
    return False

def store_otp_in_session(email, otp):
    """Store OTP and related information in the session."""
    session['otp'] = otp
    session['otp_timestamp'] = time.time()
    session['email'] = email

@user_bp.route('/generate_new_otp', methods=['POST'])
@anonymous_required()
def generate_new_otp():
    try:
        email = session.get('email')
        if not email:
            return jsonify({'error': 'Session expired. Please log in again.'}), 401

        otp = generate_otp()
        store_otp_in_session(email, otp)
        
        if send_otp_email(email, otp):
            current_app.logger.info(f"Generated new OTP and set to {email}")
            return jsonify({'message': 'A new OTP has been sent to your email.'}), 200
        else:
            return jsonify({'error': 'Failed to send new OTP email.'}), 500
    except Exception as e:
        current_app.logger.error(f"Error in generate_new_otp: {str(e)}")
        return jsonify({'error': 'Failed to generate new OTP.'}), 500

@user_bp.route('/buyerlogin', methods=['POST'])
@anonymous_required()
def buyerlogin():    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        captcha_input = data.get('captcha')
        
        current_app.logger.debug(f"captcha_input: {captcha_input}")

        if not validate_captcha(captcha_input):
            return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400

        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            conn.close()

            if user and checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session['otp_data'] = data
                session['purpose'] = 'login'
                otp = generate_otp()
                store_otp_in_session(email, otp)
                if send_otp_email(email, otp):
                    return jsonify({'redirect_url': url_for('user.verify_otp_route')}), 200
                else:
                    return jsonify({'error': 'Failed to send OTP email.'}), 500
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
        else:
            return jsonify({'error': 'Failed to connect to database'}), 500
    except Exception as e:
        current_app.logger.error(f"Error in buyerlogin: {str(e)}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/buyersignup', methods=['POST'])
@anonymous_required()
def buyersignup():
    try:
        data = request.get_json()
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        phone_num = data.get('phone_num')
        username = data.get('username')
        password = data.get('password')
        captcha_input = data.get('captcha')

        # Validate CAPTCHA
        if captcha_input != session.get('captcha_text'):
            return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400
        
        # Basic server-side validation
        if not (fname and lname and email and username and password):
            return jsonify({'error': 'All fields except phone number are required'}), 400
        

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

            # Store user data in session for OTP verification
            session['otp_data'] = data
            session['otp_role'] = 'buyer'
            session['purpose'] = 'signup'
            session['otp_timestamp'] = time.time()
                
            
            # Generate OTP and send email
            otp = generate_otp()
            
            session['otp'] = otp
            session['otp_expiry'] = datetime.utcnow() + timedelta(seconds=60)
            session['email'] = email
            
            if send_otp_email(email, otp):
                return jsonify({'redirect_url': url_for('user.verify_otp_route')}), 200
            else:
                return jsonify({'error': 'Failed to send OTP email.'}), 500
            
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {err}"}), 500
    except Exception as e:
        current_app.logger.error(f"Error in buyersignup: {e}" )
        return jsonify({'error': str(e)}), 500

@user_bp.route('/sellersignup', methods=['POST'])
@anonymous_required()
def sellersignup():
    try:
        data = request.get_json()
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        phone_num = data.get('phone_num')
        username = data.get('username')
        password = data.get('password')
        captcha_input = data.get('captcha')

        # Validate CAPTCHA
        if captcha_input != session.get('captcha_text'):
            return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400
        
        # Basic server-side validation
        if not (fname and lname and email and username and password):
            return jsonify({'error': 'All fields except phone number are required'}), 400
        

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

            # Store user data in session for OTP verification
            session['otp_data'] = data
            session['otp_role'] = 'seller'
            session['purpose'] = 'signup'
            session['otp_timestamp'] = time.time()
                
            
            # Generate OTP and send email
            otp = generate_otp()
            
            session['otp'] = otp
            session['otp_expiry'] = datetime.utcnow() + timedelta(seconds=60)
            session['email'] = email
            
            if send_otp_email(email, otp):
                return jsonify({'redirect_url': url_for('user.verify_otp_route')}), 200
            else:
                return jsonify({'error': 'Failed to send OTP email.'}), 500
            
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {err}"}), 500
    except Exception as e:
        current_app.logger.error(f"Error in sellersignup: {e}" )
        return jsonify({'error': str(e)}), 500

@user_bp.route('/verify_otp')
@anonymous_required()
def verify_otp_route():
    purpose = session.get('purpose')
    data = session.get('otp_data')
    role = session.get('otp_role')
    return render_template('util-templates/verify_otp.html', purpose=purpose, role=role, data=data)


@user_bp.route('/signup_verify_otp', methods=['POST'])
@anonymous_required()
def signup_verify_otp():
    try:
        userdata = session.get('otp_data')
        password = userdata['password']
        # Hash the password before saving
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        otpdata = request.get_json()
        role = session.get('otp_role')
        if validate_otp(otpdata):
            conn = get_mysql_connection()
            if conn:
                cursor = conn.cursor()
                insert_query = """
                INSERT INTO users (fname, lname, email, phone_num, username, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    userdata['fname'], userdata['lname'], userdata['email'],
                    userdata['phone_num'], userdata['username'],
                    hashed_password, role
                ))
                conn.commit()
                cursor.close()
                conn.close()
                
                current_app.logger.info(f"User {userdata['email']} successfully signed up")
                return jsonify({'redirect_url': url_for('main.login')}), 200
            else:
                return jsonify({'error': 'Failed to connect to database'}), 500
        else:
            return jsonify({'error': 'Invalid or expired OTP. Please try again.'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Error in signup_verify_otp: {str(e)}")
        return jsonify({'error': 'Failed to verify OTP.'}), 500
    
@user_bp.route('/login_verify_otp', methods=['POST'])
@anonymous_required()
def login_verify_otp():
    try:
        userdata = session.get('otp_data')
        email = userdata['email']
        password = userdata['password']
        otpdata = request.get_json()
        
        if validate_otp(otpdata):
            conn = get_mysql_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                user = cursor.fetchone()
                conn.close()
                
                login_user(User(user), remember=True)
                session.permanent = True
                current_app.logger.info(f"Logged in user {email}")
                                    
                return jsonify({'redirect_url': url_for('main.index')}), 200
            else:
                return jsonify({'error': 'Failed to connect to database'}), 500
        else:
            return jsonify({'error': 'Invalid or expired OTP. Please try again.'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Error in login_verify_otp: {str(e)}")
        return jsonify({'error': 'Failed to verify OTP.'}), 500


# Define the route for the user profile page
@user_bp.route("/profile")
@login_required
def profile():
    user_data = {
        'username': current_user.username,
        'fname': current_user.fname,
        'lname': current_user.lname,
        'email': current_user.email,
        'phone_num': current_user.phone_num
    }
    user_role = current_user.get_role() if current_user.is_authenticated else 'Guest'
    return render_template("util-templates/profile.html", user_data=user_data, user_role=user_role)  # Render profile.html with the userid

@user_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        fname = data.get('fname')
        lname = data.get('lname')
        phone_num = data.get('phone_num')
        
        # Basic server-side validation
        if not (fname and lname):
            return jsonify({'error': 'First name and Last name are required'}), 400

        user_id = current_user.id
        
        # Update user data in the database
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            update_query = """
            UPDATE users 
            SET fname = %s, lname = %s, phone_num = %s 
            WHERE id = %s
            """
            cursor.execute(update_query, (fname, lname, phone_num, user_id))
            conn.commit()
            conn.close()
            current_app.logger.info(f"User {current_user.id} updated profile")
            return jsonify({'message': 'User information updated successfully'})
        else:
            return jsonify({'error': 'Failed to connect to database'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error in update_profile for userid {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/generate_captcha')
def generate_captcha():
    image = ImageCaptcha()
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    data = image.generate(captcha_text)
    image_data = io.BytesIO(data.read())
    session['captcha_text'] = captcha_text
    current_app.logger.debug(f"Generated CAPTCHA text: {captcha_text}")
    return send_file(image_data, mimetype='image/png')


@user_bp.route("/seller-listings", methods=["GET"])
@seller_required()
@login_required
def seller_listings():
    sort_option = request.args.get('sort', 'none')
    category = request.args.get('category', 'all')
    seller_listings = Listing_Modules.fetch_seller_listings(current_user.id, sort_option, category)
    category_counts = Buyer_Shop.fetch_category_counts(current_user.id)
    return render_template("seller-templates/seller-listings.html", seller_listings=seller_listings, sort_option=sort_option, category=category, category_counts=category_counts)

@user_bp.route("/seller-listing-add")
@seller_required()
@login_required
def seller_listing_add():
    return render_template("seller-templates/seller-listing-add.html")  # Render seller-listings.html with the userid


@user_bp.route('/add-listing', methods=['POST'])
@seller_required()
@login_required
def add_listing():
    try:
        # Access form data using request.form and request.files
        title = request.form['title']
        description = request.form['description']
        keywords_str = request.form['keywords']  # Assuming keywords is a comma-separated string
        keywords = json.dumps(keywords_str.split(','))  # Convert to JSON array
        release_date = request.form['release_date']
        author = request.form['author']
        publisher = request.form['publisher']
        price = request.form['price']
        sales = request.form.get('sales', '0')  # Default value for sales if not provided
        stock = request.form['stock']
        type = request.form['type']
        seller_id = current_user.id  # Assuming you have a logged-in user with an 'id' attribute
        image = request.files['image']  # Handle file upload separately if needed

        # Log received data for debugging
        # current_app.logger.debug(f"Received data: title={title}, description={description}, keywords={keywords}, release_date={release_date}, author={author}, publisher={publisher}, price={price}, sales={sales}, stock={stock}, type={type}, seller_id={seller_id}, image={image.filename if image else 'None'}")
        
        # Basic server-side validation
        if not (title and price and stock and type and image):
            return jsonify({'error': 'Title, price, stock, type, and image are required fields.'}), 400
        
        # Save image to filesystem
        image_path = save_image(image)

        # Insert new listing into the database using direct MySQL connection
        conn = get_mysql_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO listings (title, description, keywords, release_date, author, publisher, price, sales, stock, type, seller_id, imagepath)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (title, description, keywords, release_date, author, publisher, price, sales, stock, type, seller_id, image_path))
        conn.commit()
        conn.close()
        
        current_app.logger.info(f"Seller {seller_id} added a listing")

        return jsonify({'message': 'Listing added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def save_image(image):
    # Define the directory where you want to save images
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'listingpictures')
    
    # Ensure the upload directory exists
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Save the image with a secure filename to the upload directory
    filename = secure_filename(image.filename)
    image_path = os.path.join(upload_dir, filename)
    image.save(image_path)

    return image_path

@user_bp.route("/add-to-cart/<int:listing_id>", methods=["POST"])
@buyer_required()
@login_required
def add_to_cart_route(listing_id):
    try:
        user_id = current_user.id
        # current_app.logger.debug(f"User {user_id} is adding listing {listing_id} to cart")
        result = Buyer_Cart.add_to_cart(user_id, listing_id)
        
        if 'error' in result:
            current_app.logger.error(result['error'])
            flash(result['error'], 'danger')
            return jsonify({'error': result['error']}), 500
        else:
            current_app.logger.info(f"User {current_user.id} added item {listing_id} to cart")
            flash(result['message'], 'success')
            return jsonify({'message': result['message']}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error adding item to cart: {str(e)}")
        flash(str(e), 'danger')
        return jsonify({'error': 'Failed to add item to cart'}), 500
    
    
@user_bp.route("/add-to-wishlist/<int:listing_id>", methods=["POST"])
@buyer_required()
@login_required
def add_to_wishlist_route(listing_id):
    try:
        user_id = current_user.id
        # current_app.logger.debug(f"User {user_id} is adding listing {listing_id} to wishlist")
        result = Buyer_Wishlist.add_to_wishlist(user_id, listing_id)
        
        if 'error' in result:
            current_app.logger.error(result['error'])
            flash(result['error'], 'danger')
            return jsonify({'error': result['error']}), 500
        else:
            current_app.logger.info(f"User {current_user.id} added item {listing_id} to wishlist")
            flash(result['message'], 'success')
            return jsonify({'message': result['message']}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error adding item to wishlist: {str(e)}")
        flash(str(e), 'danger')
        return jsonify({'error': 'Failed to add item to wishlist'}), 500

@user_bp.route('/edit-listing/<int:item_id>', methods=['POST'])
@seller_required()
@login_required
def edit_listing(item_id):
    try:
        # Access form data using request.form
        title = request.form['title']
        description = request.form['description']
        keywords_str = request.form['keywords']
        keywords = json.dumps(keywords_str.split(','))  # Convert to JSON array
        release_date = request.form['release_date']
        author = request.form['author']
        publisher = request.form['publisher']
        price = request.form['price']
        stock = request.form['stock']
        type = request.form['type']

        # Basic server-side validation
        if not (title and price and stock and type):
            return jsonify({'error': 'Title, price, stock, and type are required fields.'}), 400

        # Fetch the listing to verify the seller
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT seller_id FROM listings WHERE id = %s"
        cursor.execute(query, (item_id,))
        listing = cursor.fetchone()
        conn.close()

        if not listing:
            return jsonify({'error': 'Listing not found'}), 404

        if listing['seller_id'] != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403

        # Update listing in the database using direct MySQL connection
        conn = get_mysql_connection()
        cursor = conn.cursor()

        update_query = """
        UPDATE listings 
        SET title = %s, description = %s, keywords = %s, release_date = %s, author = %s, publisher = %s, price = %s, stock = %s, type = %s 
        WHERE id = %s AND seller_id = %s
        """
        cursor.execute(update_query, (title, description, keywords, release_date, author, publisher, price, stock, type, item_id, current_user.id))
        conn.commit()
        conn.close()

        current_app.logger.info(f"Seller {current_user.id} edited listing {listing_id}")
        return '', 200
    except Exception as e:
        current_app.logger.error(f"Error in edit_listing: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_bp.route("/delete-listing/<int:listing_id>", methods=["DELETE"])
@seller_required()
@login_required
def delete_listing(listing_id):
    try:
        listing = Listing_Modules.get_listing_byid(listing_id)
        if not listing:
            return jsonify({"success": False, "message": "Listing not found"}), 404

        # Assuming listing is a dictionary-like object returned from SQLAlchemy
        if listing['seller_id'] != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        # Fetch the image path before deleting the listing
        image_path = listing['imagepath']
        
        Listing_Modules.delete_listing_fromdb(listing_id)
        
        # Delete the image file from the filesystem
        if image_path:
            delete_image(image_path)
            
        current_app.logger.info(f"Seller {current_user.id} deleted listing {listing_id}")
        return jsonify({"success": True}), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting listing {listing_id}: {e}")
        return jsonify({"success": False, "message": "Failed to delete the listing"}), 500
    
def delete_image(image_path):
    
    # Remove '/app' prefix from the image path if it exists
    # if image_path.startswith('/app'):
    #     image_path = image_path.replace('/app', '')
        
    # Ensure the image path is valid and remove the file
    current_app.logger.info(f"Deleting image with path {image_path}")
    if os.path.exists(image_path):
        os.remove(image_path)
       
@user_bp.route('/item/<int:item_id>')
@non_admin_required()
def item_page(item_id):
    try:
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM listings WHERE id = %s"
            cursor.execute(query, (item_id,))
            item = cursor.fetchone()
            seller_name_query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(seller_name_query, (item['seller_id'],))
            seller = cursor.fetchone()
            seller_name = seller['fname'] + " " + seller['lname']
            
            comments_query = f""" SELECT c.id, c.title, c.body, c.rating, c.created_at, u.username, u.fname, u.lname FROM comments c JOIN users u ON c.user_id = u.id WHERE c.listing_id = {item_id} """
            
            cursor.execute(comments_query)
            comments = cursor.fetchall()
            # current_app.logger.debug(comments)
            
            conn.close()

            return render_template('buyer-templates/buyer-itempage.html', item=item, seller_name=seller_name, comments=comments)

        else:
            flash('Failed to connect to database', 'danger')
            return redirect(url_for('main.shop'))

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        current_app.logger.error(f"Error in fetching item page with {item_id}: {str(e)}")
        return redirect(url_for('main.shop'))
    
@user_bp.route('/selleritem/<int:item_id>')
@seller_required()
@login_required
def item_page_seller(item_id):
    try:
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM listings WHERE id = %s"
            cursor.execute(query, (item_id,))
            item = cursor.fetchone()
            seller_name_query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(seller_name_query, (item['seller_id'],))
            seller = cursor.fetchone()
            seller_name = seller['fname'] + " " + seller['lname']
            
            comments_query = f""" SELECT c.id, c.title, c.body, c.rating, c.created_at, u.username, u.fname, u.lname FROM comments c JOIN users u ON c.user_id = u.id WHERE c.listing_id = {item_id} """
            
            cursor.execute(comments_query)
            comments = cursor.fetchall()
            # current_app.logger.debug(comments)
            
            conn.close()

            return render_template('seller-templates/seller-itempage.html', item=item, seller_name=seller_name, comments=comments)

        else:
            flash('Failed to connect to database', 'danger')
            return redirect(url_for('main.shop'))

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        current_app.logger.error(f"Error in selleritem with item_id {item_id}: {str(e)}")
        return redirect(url_for('main.shop'))
    
@user_bp.route('/cart')
@buyer_required()
@login_required
def cart():
    cart_items = get_cart_items(current_user.id)
    cart_value = Buyer_Cart.get_user_cart_value(current_user.id)
    return render_template('buyer-templates/buyer-cart.html', cart_items=cart_items, cart_value=cart_value)

@user_bp.route('/cart/increase/<int:cart_item_id>', methods=['POST'])
@buyer_required()
@login_required
def increase_quantity(cart_item_id):
    result = Buyer_Cart.increase_cart_item_quantity(cart_item_id, current_user.id)
    if result['success']:
        current_app.logger.info(f"User {current_user.id} increased card item {cart_item_id}'s quantity")
        return jsonify({'message': 'Quantity increased successfully'}), 200
    else:
        current_app.logger.error(f"Error in cart increase user_id {current_user.id} and cart_item_id {cart_item_id}: {str(e)}")
        return jsonify({'error': result['error']}), 400

@user_bp.route('/cart/decrease/<int:cart_item_id>', methods=['POST'])
@buyer_required()
@login_required
def decrease_quantity(cart_item_id):
    result = Buyer_Cart.decrease_cart_item_quantity(cart_item_id, current_user.id)
    if result['success']:
        current_app.logger.info(f"User {current_user.id} decreased card item {cart_item_id}'s quantity")
        return jsonify({'message': 'Quantity decreased successfully'}), 200
    else:
        current_app.logger.error(f"Error in cart decrease user_id {current_user.id} and cart_item_id {cart_item_id}: {str(e)}")
        return jsonify({'error': result['error']}), 400

@user_bp.route('/cart/delete/<int:cart_item_id>', methods=['POST'])
@buyer_required()
@login_required
def delete_item(cart_item_id):
    result = Buyer_Cart.delete_cart_item(cart_item_id, current_user.id)
    if result['success']:
        current_app.logger.info(f"User {current_user.id} deleted cart item {cart_item_id}")
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in cart item delete user_id {current_user.id} and cart_item_id {cart_item_id}: {str(e)}")
        return jsonify({'error': result['error']}), 400
    
@user_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f"Logging out {current_user.id}")
    logout_user()
    session.pop('user_id', None)  # Clear the 'user_id' from session
    return redirect(url_for('main.index'))  # Redirect to index page after logout

@user_bp.route("/wishlist")
@buyer_required()
@login_required
def wishlist():
    wishlist_items = Buyer_Wishlist.get_wishlist_items(current_user.id)
    return render_template("buyer-templates/buyer-wishlist.html", wishlist_items=wishlist_items)  # Render the /wishlist template

@user_bp.route('/wishlist/delete/<int:wishlist_item_id>', methods=['POST'])
@buyer_required()
@login_required
def delete_item_wishlist(wishlist_item_id):
    result = Buyer_Wishlist.delete_wishlist_item(wishlist_item_id, current_user.id)
    if result['success']:
        current_app.logger.info(f"User {current_user.id} deleted wishlist item {wishlist_item_id}")
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        current_app.logger.error(f"Error in wishklist item delete user_id {current_user.id} and wishlist_item_id {wishlist_item_id}: {str(e)}")
        return jsonify({'error': result['error']}), 400
    
    
@user_bp.route('/report-item', methods=['POST'])
@login_required
def report_item():
    try:
        data = request.get_json()
        title = data.get('title')
        body = data.get('body')
        item_id = data.get('item_id')
        seller_id = data.get('seller_id')
        buyer_id = data.get('buyer_id')
        captcha_input = data.get('captcha')
        # Verify CAPTCHA
        if captcha_input != session.get('captcha_text'):
            return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400
        
        # current_app.logger.debug(f"Received in user.py title: {title}, body: {body}, item_id: {item_id}, seller_id: {seller_id}, buyer_id: {buyer_id}")
        
        result = create_report(title, body, item_id, seller_id, buyer_id)
        
        if 'error' in result:
            current_app.logger.error(f"Error in create_report function: {result['error']}")
            return jsonify({'error': result['error']}), 500
        else:
            current_app.logger.info(f"User {current_user.id} reported item {item_id}")
            return jsonify({'message': result['message']}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in report_item route: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@user_bp.route('/seller/<int:seller_id>')
@non_admin_required()
def buyer_seller_page(seller_id):
    seller_info = get_seller_info(seller_id)
    sort_option = request.args.get('sort', 'none')
    category = request.args.get('category', 'all')
    listings = Listing_Modules.fetch_seller_listings(seller_id, sort_option, category)
    category_counts = Buyer_Shop.fetch_category_counts_for_shop_buyer()
    return render_template('buyer-templates/buyer-sellerpage.html', seller_info=seller_info, listings=listings, sort_option=sort_option, category=category, category_counts=category_counts)

@user_bp.route('/submit-comment/<int:item_id>', methods=['POST'])
@login_required
def submit_comment(item_id):
    try:
        title = request.form.get('title')
        body = request.form.get('body')
        rating = int(request.form.get('rating'))
        user_id = current_user.id  # Assuming you have a way to get the current user ID

        # current_app.logger.debug(f"Received title: {title}, body: {body}, rating: {rating}, user_id: {user_id}, item_id: {item_id}")

        # Validate rating
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        # Create the comment
        result = create_comment(title, body, rating, item_id, user_id)

        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        else:
            current_app.logger.info(f"User {current_user.id} commented on item {item_id}")
            # On success, do not return JSON but allow the frontend to reload
            return '', 200

    except Exception as e:
        current_app.logger.error(f"Error in submit_comment route: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@user_bp.route('/report-comment/<int:comment_id>', methods=['POST'])
@login_required
def report_comment(comment_id):
    title = request.form.get('title')
    body = request.form.get('body')
    captcha_input = request.form.get('captcha')
    reporter_id = current_user.id  # Assuming you have a way to get the current logged-in user's ID
    
    # current_app.logger.debug(f"report comment route called comment id: {comment_id} title: {title} body: {body} captcha_input: {captcha_input} reporter_id: {reporter_id}")
    
    # Verify CAPTCHA
    if captcha_input != session.get('captcha_text'):
        flash('Invalid CAPTCHA. Please try again.', 'danger')
        return redirect(request.referrer or url_for('main.shop'))
    
    try:
        result = create_comment_report(comment_id, reporter_id, title, body)
        if 'error' in result:
            flash(result['error'], 'danger')
        else:
            current_app.logger.info(f"User {reporter_id} reported {comment_id}")
            flash('Report submitted successfully.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error reporting comment: {str(e)}")
        flash(f"Error reporting comment: {str(e)}", 'danger')
    
    return redirect(request.referrer or url_for('main.shop'))

# @user_bp.route('/payment', methods=['POST'])
# @login_required
# def payment():
#     try:
#         # Fetch the cart value from the session or calculate it based on the current user
#         cart_value = get_user_cart_value(current_user.id)

#         if not cart_value or cart_value <= 0:
#             current_app.logger.error("Invalid cart value.")
#             return "Invalid cart value.", 400

#         # Convert cart value to cents
#         amount = int(cart_value * 100)

#         data = request.form

#         address = {
#             "line1": data.get('address_line1'),
#             "line2": data.get('address_line2'),
#             "city": data.get('city'),
#             "state": data.get('state'),
#             "postal_code": data.get('postal_code'),
#             "country": data.get('country')
#         }

#         customer = stripe.Customer.create(
#             email=data.get('stripeEmail'),
#             source=data.get('stripeToken'),
#             address=address  # Add address to the customer creation
#         )

#         charge = stripe.Charge.create(
#             customer=customer.id,
#             description='BookWise Purchase',
#             amount=amount,
#             currency='sgd',
#         )

#         # Create a new transaction record
#         transaction_id = create_transaction(current_user.id, 'completed')

#         # Create a new order record
#         create_order(transaction_id, cart_value, current_user.id)

#         # Clear the cart after successful purchase
#         clear_cart(current_user.id)

#         return redirect(url_for('user.success'))

#     except Exception as e:
#         current_app.logger.error(f"Error during payment: {e}")
#         return f"Internal Server Error: {e}", 500


@user_bp.route('/payment', methods=['POST'])
@buyer_required()
@login_required
def payment():
    current_app.logger.info(f"Payment route called for {current_user.id}")
    try:
        # Fetch the cart value from the session or calculate it based on the current user
        cart_value = Buyer_Cart.get_user_cart_value(current_user.id)
        cart_items = get_user_cart_items(current_user.id)

        if not cart_value or cart_value <= 0:
            current_app.logger.error(f"Invalid cart value {cart_value} and user_id {current_user.id}")
            return "Invalid cart value.", 400

        # Convert cart value to cents
        amount = int(cart_value * 100)

        data = request.form

        address = {
            "line1": data.get('address_line1'),
            "line2": data.get('address_line2'),
            "city": data.get('city'),
            "state": data.get('state'),
            "postal_code": data.get('postal_code'),
            "country": data.get('country')
        }

        customer = stripe.Customer.create(
            email=data.get('stripeEmail'),
            source=data.get('stripeToken'),
            address=address  # Add address to the customer creation
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            description='BookWise Purchase',
            amount=amount,
            currency='sgd',
        )

        # Update stock quantities
        engine = get_engine()
        with engine.connect() as conn:
            for item in cart_items:
                update_stock_query = text("""
                    UPDATE listings
                    SET stock = stock - :quantity, sales = sales + :quantity
                    WHERE id = :listing_id
                """)
                conn.execute(update_stock_query, {'quantity': item['quantity'], 'listing_id': item['listing_id']})

        # Create a new transaction record
        transaction_id = create_transaction(current_user.id, 'completed')

        # Create a new order record
        create_order(transaction_id, cart_value, current_user.id)

        # Clear the cart after successful purchase
        clear_cart(current_user.id)
        
        engine.dispose

        return redirect(url_for('user.success'))

    except Exception as e:
        current_app.logger.error(f"Error during payment: {e}")
        return f"Internal Server Error: {e}", 500

    
def clear_user_cart(user_id):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            delete_query = text("""
                DELETE ci
                FROM cart_items ci
                JOIN carts c ON ci.cart_id = c.id
                WHERE c.user_id = :user_id
            """)
            conn.execute(delete_query, {'user_id': user_id})
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error clearing user cart: {e}")


def get_user_cart_items(user_id):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT ci.id, l.imagepath, l.title, l.price, ci.quantity, ci.listing_id
                FROM cart_items ci
                JOIN listings l ON ci.listing_id = l.id
                JOIN carts c ON ci.cart_id = c.id
                WHERE c.user_id = :user_id
            """)
            result = conn.execute(query, {'user_id': user_id})
            
            return [dict(row) for row in result]
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching cart items: {e}")
        return []


def create_transaction(user_id, status):
    engine = get_engine()
    try:
        query = """
            INSERT INTO transactions (user_id, status)
            VALUES (%s, %s)
        """
        with engine.connect() as conn:
            result = conn.execute(query, (user_id, status))
            transaction_id = result.lastrowid
            
        current_app.logger.info(f"Transaction created with transaction id {transaction_id} with user id {current_user.id}")
        return transaction_id
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error creating transaction: {e}")
        return None
    finally:
        engine.dispose()

def create_order(transaction_id, total_price, buyer_id):
    engine = get_engine()
    try:
        query = text("""
            INSERT INTO orders (transaction_id, keywords, total_price, buyer_id, quantity)
            VALUES (:transaction_id, :keywords, :total_price, :buyer_id, :quantity)
        """)
        # Calculate total quantity and gather keywords from cart items
        cart_items = get_cart_items(buyer_id)
        quantity = sum(item['quantity'] for item in cart_items)
        keywords = [item['keywords'] for item in cart_items]
        keywords_json = json.dumps(keywords)  # Ensure proper JSON serialization

        # Print the serialized JSON for debugging
        # current_app.logger.debug(f"Serialized keywords JSON: {keywords_json}")

        with engine.connect() as conn:
            conn.execute(query, {
                'transaction_id': transaction_id,
                'keywords': keywords_json,
                'total_price': total_price,
                'buyer_id': buyer_id,
                'quantity': quantity
            })
            
            current_app.logger.info(f"Order created for transaction id {transaction_id}, user id {buyer_id}")
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error creating order: {e}")
    finally:
        engine.dispose()



def calculate_total_quantity(user_id):
    cart_items = get_cart_items(user_id)
    total_quantity = sum(item['quantity'] for item in cart_items)
    return total_quantity

def clear_cart(user_id):
    current_app.logger.info(f"Clear cart route called for user {current_user.id}")
    engine = get_engine()
    try:
        # Get the user's cart
        user_cart = Buyer_Cart.get_user_cart(user_id)
        if not user_cart:
            return {'success': False, 'error': 'Cart not found'}

        cart_id = user_cart['id']

        # Delete all items in the cart
        delete_items_query = f"DELETE FROM cart_items WHERE cart_id = '{cart_id}'"
        engine.execute(delete_items_query)

        # Reset the cart item count and total price
        reset_cart_query = f"UPDATE carts SET item_count = 0, total_price = 0.0 WHERE id = '{cart_id}'"
        engine.execute(reset_cart_query)
        
        return {'success': True}
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error clearing cart for user_id {user_id}: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()

@user_bp.route('/clear_cart', methods=['POST'])
@buyer_required()
@login_required
def clear_cart_route():
    try:
        result = clear_cart(current_user.id)
        if result['success']:
            return jsonify({'message': 'Cart cleared successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 500
    except Exception as e:
        current_app.logger.error(f"Error in clear cart route: {e}")
        return jsonify({'error': str(e)}), 500

def get_cart_items(buyer_id):
    engine = get_engine()
    try:
        query = """
            SELECT ci.id, l.imagepath, l.title, l.price, ci.quantity, l.keywords
            FROM cart_items ci
            JOIN listings l ON ci.listing_id = l.id
            JOIN carts c ON ci.cart_id = c.id
            WHERE c.user_id = %s
        """
        with engine.connect() as conn:
            result = conn.execute(query, (buyer_id,))
            cart_items = [dict(row) for row in result]
        
        current_app.logger.info(f"Got cart items for user {buyer_id}")
        return cart_items
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching cart items for user_id {buyer_id}: {e}")
        return []
    finally:
        engine.dispose()


@user_bp.route('/success')
@login_required
def success():
    current_app.logger.info(f"Success for user {current_user.id}")
    clear_cart(current_user.id)
    return render_template('util-templates/success.html')

@user_bp.route("/cancel")
@login_required
def cancel():
    current_app.logger.info(f"Cancelled for user {current_user.id}")
    return render_template ('cancel.html')


@user_bp.context_processor
def inject_user_cart_count():
    if current_user.is_authenticated:
        cart = Buyer_Cart.get_user_cart(current_user.id)
        user_cart_count = cart['item_count'] if cart else 0
    else:
        user_cart_count = 0
    return dict(user_cart_count=user_cart_count)