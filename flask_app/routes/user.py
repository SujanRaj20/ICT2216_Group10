from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect,flash,current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from SqlAlchemy.createTable import User

from bcrypt import hashpw, gensalt, checkpw
import bcrypt  # Import bcrypt module directly
import mysql.connector
from db_connector import get_mysql_connection

# Create a Blueprint named 'user'
user_bp = Blueprint('user', __name__)



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
    return render_template("buyer-account.html", user_data=user_data)  # Render profile.html with the userid

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

@user_bp.route("/seller-listings")
def listings():
    return render_template("seller-listings.html")  # Render seller-listings.html with the userid

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
       


@user_bp.route('/buyerlogin',methods=['GET', 'POST'])
def buyerlogin():
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
                    login_user(User(user), remember=True)  # Login the user
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
def cart():
    # Your logic to handle the cart view
    return render_template('cart.html', userid=userid)
    
    
@user_bp.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None)  # Clear the 'user_id' from session
    return redirect(url_for('main.index'))  # Redirect to index page after logout

