from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect,flash,current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from SqlAlchemy.createTable import User, fetch_seller_listings, get_listing_byid, delete_listing_fromdb, fetch_category_counts, add_to_cart, get_cart_items, increase_cart_item_quantity, decrease_cart_item_quantity, delete_cart_item, get_user_cart_value, add_to_wishlist, get_wishlist_items,delete_wishlist_item
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

# Create a Blueprint named 'user'
user_bp = Blueprint('user', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG


# Define the route for the user profile page
@user_bp.route("/profile")
# @login_required
def profile():
    user_data = {
        'username': current_user.username,
        'fname': current_user.fname,
        'lname': current_user.lname,
        'email': current_user.email,
        'phone_num': current_user.phone_num
    }
    user_role = current_user.get_role() if current_user.is_authenticated else 'Guest'
    return render_template("profile.html", user_data=user_data, user_role=user_role)  # Render profile.html with the userid

@user_bp.route('/update_profile', methods=['POST'])
# @login_required
def update_profile():
    try:
        data = request.get_json()
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        phone_num = data.get('phone_num')
        username = data.get('username')
        
        # Basic server-side validation
        if not (fname and lname and email and username):
            return jsonify({'error': 'All fields except phone number are required'}), 400
        
        # Update user data in the database
        current_user.fname = fname
        current_user.lname = lname
        current_user.email = email
        current_user.phone_num = phone_num
        current_user.username = username
        db.session.commit()  # Commit changes to the database
        
        return jsonify({'message': 'User information updated successfully'})
    
    except Exception as e:
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
@login_required
def seller_listings():
    sort_option = request.args.get('sort', 'none')
    category = request.args.get('category', 'all')
    seller_listings = fetch_seller_listings(current_user.id, sort_option, category)
    category_counts = fetch_category_counts(current_user.id)
    return render_template("seller-listings.html", seller_listings=seller_listings, sort_option=sort_option, category=category, category_counts=category_counts)

@user_bp.route("/seller-listing-add")
def seller_listing_add():
    return render_template("seller-listing-add.html")  # Render seller-listings.html with the userid

@user_bp.route('/add-listing', methods=['POST'])
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
        stock = request.form['stock']
        type = request.form['type']
        seller_id = current_user.id  # Assuming you have a logged-in user with an 'id' attribute
        image = request.files['image']  # Handle file upload separately if needed
        
        # Basic server-side validation
        if not (title and price and stock and type and image):
            return jsonify({'error': 'Title, price, stock, type, and image are required fields.'}), 400
        
        # Save image to filesystem
        image_path = save_image(image)

        # Insert new listing into the database using direct MySQL connection
        conn = get_mysql_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO listings (title, description, keywords, release_date, author, publisher, price, stock, type, seller_id, imagepath)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (title, description, keywords, release_date, author, publisher, price, stock, type, seller_id, image_path))
        conn.commit()
        conn.close()

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
@login_required
def add_to_cart_route(listing_id):
    try:
        user_id = current_user.id
        current_app.logger.debug(f"User {user_id} is adding listing {listing_id} to cart")
        result = add_to_cart(user_id, listing_id)
        
        if 'error' in result:
            current_app.logger.error(result['error'])
            flash(result['error'], 'danger')
            return jsonify({'error': result['error']}), 500
        else:
            current_app.logger.debug(result['message'])
            flash(result['message'], 'success')
            return jsonify({'message': result['message']}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error adding item to cart: {str(e)}")
        flash(str(e), 'danger')
        return jsonify({'error': 'Failed to add item to cart'}), 500
    
    
@user_bp.route("/add-to-wishlist/<int:listing_id>", methods=["POST"])
@login_required
def add_to_wishlist_route(listing_id):
    try:
        user_id = current_user.id
        current_app.logger.debug(f"User {user_id} is adding listing {listing_id} to wishlist")
        result = add_to_wishlist(user_id, listing_id)
        
        if 'error' in result:
            current_app.logger.error(result['error'])
            flash(result['error'], 'danger')
            return jsonify({'error': result['error']}), 500
        else:
            current_app.logger.debug(result['message'])
            flash(result['message'], 'success')
            return jsonify({'message': result['message']}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error adding item to wishlist: {str(e)}")
        flash(str(e), 'danger')
        return jsonify({'error': 'Failed to add item to wishlist'}), 500

@user_bp.route("/delete-listing/<int:listing_id>", methods=["DELETE"])
@login_required
def delete_listing(listing_id):
    try:
        listing = get_listing_byid(listing_id)
        if not listing:
            return jsonify({"success": False, "message": "Listing not found"}), 404

        # Assuming listing is a dictionary-like object returned from SQLAlchemy
        if listing['seller_id'] != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        # Fetch the image path before deleting the listing
        image_path = listing['imagepath']
        
        delete_listing_fromdb(listing_id)
        
        # Delete the image file from the filesystem
        if image_path:
            delete_image(image_path)
        
        return jsonify({"success": True}), 200
    except Exception as e:
        logging.error(f"Error deleting listing {listing_id}: {e}")
        return jsonify({"success": False, "message": "Failed to delete the listing"}), 500
    
def delete_image(image_path):
    
    # Remove '/app' prefix from the image path if it exists
    # if image_path.startswith('/app'):
    #     image_path = image_path.replace('/app', '')
        
    # Ensure the image path is valid and remove the file
    if os.path.exists(image_path):
        os.remove(image_path)


@user_bp.route('/buyersignup', methods=['POST'])
def buyersignup():
    try:
        data = request.get_json()
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        phone_num = data.get('phone_num')
        username = data.get('username')
        password = data.get('password')
        role = 'buyer'
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
       


@user_bp.route('/buyerlogin', methods=['GET', 'POST'])
def buyerlogin():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            captcha_input = request.form.get('captcha')
            
            # current_app.logger.debug(f"User credentials are email: {email} password: {password}")

            # current_app.logger.debug(f"User entered CAPTCHA: {captcha_input}")
            # current_app.logger.debug(f"Session CAPTCHA: {session.get('captcha_text')}")

            if captcha_input != session.get('captcha_text'):
                return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400

            conn = get_mysql_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                user = cursor.fetchone()
                conn.close()

                if user and checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    login_user(User(user), remember=True)
                    session.permanent = True
                    return jsonify({'message': 'Login successful'}) and redirect(url_for('main.index'))
                else:
                    return jsonify({'error': 'Invalid email or password'}), 401
            else:
                return jsonify({'error': 'Failed to connect to database'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405
    
@user_bp.route('/sellerlogin',methods=['GET', 'POST'])
def sellerlogin():
    if request.method == 'POST':
        try:
            # Extract email and password from request.form
            email = request.form.get('email')
            password = request.form.get('password')

            conn = get_mysql_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT * FROM users WHERE email = %s
                """
                cursor.execute(query, (email,))
                user = cursor.fetchone()

                conn.close()

                if user and checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    # Successful login
                    user_obj = User(user)
                    login_user(user_obj, remember=True)  # Login the user
                    session['user_id'] = user_obj.id
                    session.permanent = True
                    return jsonify({'message': 'Login successful'}) and redirect(url_for('main.index'))  
                    redirect
                else:
                    return jsonify({'error': 'Invalid email or password'}), 401
            else:
                return jsonify({'error': 'Failed to connect to database'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405
    
    
@user_bp.route('/sellersignup', methods=['POST'])
def sellersignup():
    try:
        data = request.get_json()
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        phone_num = data.get('phone_num')
        username = data.get('username')
        password = data.get('password')
        role = 'seller'
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
    
@user_bp.route('/cart')
@login_required
def cart():
    cart_items = get_cart_items(current_user.id)
    cart_value = get_user_cart_value(current_user.id)
    return render_template('buyer-cart.html', cart_items=cart_items, cart_value=cart_value)

@user_bp.route('/cart/increase/<int:cart_item_id>', methods=['POST'])
@login_required
def increase_quantity(cart_item_id):
    result = increase_cart_item_quantity(cart_item_id, current_user.id)
    if result['success']:
        return jsonify({'message': 'Quantity increased successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@user_bp.route('/cart/decrease/<int:cart_item_id>', methods=['POST'])
@login_required
def decrease_quantity(cart_item_id):
    result = decrease_cart_item_quantity(cart_item_id, current_user.id)
    if result['success']:
        return jsonify({'message': 'Quantity decreased successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@user_bp.route('/cart/delete/<int:cart_item_id>', methods=['POST'])
@login_required
def delete_item(cart_item_id):
    result = delete_cart_item(cart_item_id, current_user.id)
    if result['success']:
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400
    
@user_bp.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None)  # Clear the 'user_id' from session
    return redirect(url_for('main.index'))  # Redirect to index page after logout

@user_bp.route("/wishlist")
@login_required
def wishlist():
    wishlist_items = get_wishlist_items(current_user.id)
    return render_template("buyer-wishlist.html", wishlist_items=wishlist_items)  # Render the /wishlist template

@user_bp.route('/wishlist/delete/<int:wishlist_item_id>', methods=['POST'])
@login_required
def delete_item_wishlist(wishlist_item_id):
    result = delete_wishlist_item(wishlist_item_id, current_user.id)
    if result['success']:
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        return jsonify({'error': result['error']}), 400