from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect
from bcrypt import hashpw, gensalt, checkpw
import bcrypt  # Import bcrypt module directly
import mysql.connector
from db_connector import get_mysql_connection

# Create a Blueprint named 'user'
user_bp = Blueprint('user', __name__)



# Define the route for the user profile page
@user_bp.route("/user/<userid>")
def profile(userid):
    return render_template("profile.html", userid=userid)  # Render profile.html with the userid

@user_bp.route("/cart/<userid>")
def cart(userid):
    return render_template("cart.html", userid=userid)  # Render cart.html with the userid

@user_bp.route('/buyersignup', methods=['POST'])
def signup():
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
            # Example: Insert user into the database
            insert_query = """
            INSERT INTO users (fname, lname, email, phone_num, username, password_hash, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (fname, lname, email, phone_num, username, hashed_password.decode('utf-8'), role))
            conn.commit()
            conn.close()
            return jsonify({'message': 'User signed up successfully'})
        else:
            return jsonify({'error': 'Failed to connect to database'})
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {err}"})
    except Exception as e:
        return jsonify({'error': str(e)})


@user_bp.route('/buyerlogin', methods=['POST'])
def login():
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
                    session['user_id'] = user['id']  # Store user ID in session
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
    
    
@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the 'user_id' from session
    return redirect(url_for('main.index'))  # Redirect to index page after logout

