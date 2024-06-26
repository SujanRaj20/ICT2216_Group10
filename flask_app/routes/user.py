from flask import Blueprint, render_template, request, jsonify
from bcrypt import hashpw, gensalt
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
        role = data.get('buyer')
        
         # Basic server-side validation
        if not (fname and lname and email and username and password):
            return jsonify({'error': 'All fields except phone number are required'}), 400
        
        # Additional validation (e.g., email format, unique username/email check) goes here
        

        # Hash the password before saving
        hashed_password = hashpw(password.encode('utf-8'), gensalt())

        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            # Example: Insert user into the database
            insert_query = """
            INSERT INTO users (fname, lname, email, phone_num, username, password, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (fname, lname, email, phone_num, username, hashed_password, role))
            conn.commit()
            conn.close()
            return jsonify({'message': 'User signed up successfully'})
        else:
            return jsonify({'error': 'Failed to connect to database'})
    except Exception as e:
        return jsonify({'error': str(e)})