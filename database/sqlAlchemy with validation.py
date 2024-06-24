from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify
from sshtunnel import SSHTunnelForwarder
import re

# MySQL Server Parameters
mysql_host = '127.0.0.1'
mysql_port = 3306
mysql_user = 'testtoday'
mysql_password = 'kMcFNgtzJTA0{XW'
mysql_db = 'bookwise'

# SSH Tunnel Parameters
ssh_host = '3.145.129.7'
ssh_port = 22
ssh_username = 'student25'
ssh_keyfile = r'C:\Users\Sujan\OneDrive\Desktop\TRI3\ICT2216 - Secure Software Development\ICT2216-student25.pem'

app = Flask(__name__)

def setup_ssh_tunnel():
    try:
        tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_pkey=ssh_keyfile,
            remote_bind_address=(mysql_host, mysql_port),
        )
        tunnel.start()
        print(f"SSH tunnel established on local port {tunnel.local_bind_port}")
        return tunnel
    except Exception as e:
        print(f"Error establishing SSH tunnel: {e}")
        return None

def create_engine_with_tunnel():
    tunnel = setup_ssh_tunnel()
    if tunnel:
        db_uri = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{tunnel.local_bind_port}/{mysql_db}'
        engine = create_engine(db_uri)
        return engine, tunnel
    return None, None

def create_tables(engine):
    metadata = MetaData(bind=engine)

    # Define users table
    users = Table('users', metadata,
                  Column('user_id', Integer, primary_key=True, autoincrement=True),
                  Column('username', String(255), nullable=False, unique=True),
                  Column('password', String(255), nullable=False),
                  Column('fname', String(255), nullable=False),
                  Column('lname', String(255), nullable=False),
                  Column('email', String(255), nullable=False, unique=True),
                  Column('phone_num', String(255)),
                  Column('role', String(255), nullable=False, default='buyer'),
                  Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                  )

    # Define other tables...
    sessions = Table('sessions', metadata,
                     Column('session_id', Integer, primary_key=True, autoincrement=True),
                     Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
                     Column('status', String(255), nullable=False),
                     Column('session_age', Integer),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    listings = Table('listings', metadata,
                     Column('listing_id', Integer, primary_key=True, autoincrement=True),
                     Column('title', String(255), nullable=False),
                     Column('description', String(255), nullable=False),
                     Column('price', Integer, nullable=False),
                     Column('stock', Integer, nullable=False),
                     Column('rating', Integer),
                     Column('seller_id', Integer, ForeignKey('users.user_id'), nullable=False),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    pictures = Table('pictures', metadata,
                     Column('picture_id', Integer, primary_key=True, autoincrement=True),
                     Column('picture_url', String(255), nullable=False),
                     Column('listing_id', Integer, ForeignKey('listings.listing_id'), nullable=False),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    cart = Table('cart', metadata,
                 Column('cart_id', Integer, primary_key=True, autoincrement=True),
                 Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
                 Column('itemcount', Integer, nullable=False),
                 Column('totalprice', Integer, nullable=False)
                 )

    items = Table('items', metadata,
                  Column('item_id', Integer, primary_key=True, autoincrement=True),
                  Column('listing_id', Integer, ForeignKey('listings.listing_id'), nullable=False),
                  Column('cart_id', Integer, ForeignKey('cart.cart_id'))
                  )

    orders = Table('orders', metadata,
                   Column('order_id', Integer, primary_key=True, autoincrement=True),
                   Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
                   Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                   )

    transactions = Table('transactions', metadata,
                         Column('transaction_id', Integer, primary_key=True, autoincrement=True),
                         Column('order_id', Integer, ForeignKey('orders.order_id'), nullable=False),
                         Column('status', String(255), nullable=False),
                         Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                         )

    # Create all tables
    metadata.create_all()

    return metadata

@app.route('/signup', methods=['POST'])
def signup():
    return handle_signup(role='buyer')

@app.route('/signup-seller', methods=['POST'])
def signup_seller():
    return handle_signup(role='seller')

def handle_signup(role):
    data = request.json
    username = data.get('username')
    password = data.get('password')
    fname = data.get('fname')
    lname = data.get('lname')
    email = data.get('email')
    phone_num = data.get('phone_num')

    if not username or not password or not fname or not lname or not email:
        return jsonify({'error': 'All fields except phone number are required.'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long.'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    hashed_password = generate_password_hash(password)

    engine, tunnel = create_engine_with_tunnel()
    if not engine:
        return jsonify({'error': 'Database connection failed.'}), 500

    metadata = MetaData(bind=engine)
    users = Table('users', metadata, autoload=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        new_user = users.insert().values(
            username=username, 
            password=hashed_password, 
            fname=fname, 
            lname=lname, 
            email=email, 
            phone_num=phone_num,
            role=role
        )
        conn = engine.connect()
        conn.execute(new_user)
        conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()
        engine.dispose()
        if tunnel:
            tunnel.stop()

    return jsonify({'message': 'User created successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    return handle_login(role='buyer')

@app.route('/login-seller', methods=['POST'])
def login():
    return handle_login(role='seller')
def handle_login(role):
    data = request.json
    username_or_email = data.get('username')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'error': 'Username and password are required.'}), 400

    engine, tunnel = create_engine_with_tunnel()
    if not engine:
        return jsonify({'error': 'Database connection failed.'}), 500

    metadata = MetaData(bind=engine)
    users = Table('users', metadata, autoload=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(users).filter(
            (users.c.username == username_or_email) | 
            (users.c.email == username_or_email)
        ).first()

        if user and check_password_hash(user.password, password):
            if user.role == role:
                return jsonify({'message': 'Login successful.'}), 200
            else:
                return jsonify({'error': f'Invalid role for {role} login.'}), 401
        else:
            return jsonify({'error': 'Invalid username or password.'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
        engine.dispose()
        if tunnel:
            tunnel.stop()

def validate_email(email):
    re_email = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    return re_email.match(email)

def main():
    try:
        # Set up SSH tunnel
        tunnel = setup_ssh_tunnel()

        if tunnel:
            # Create SQLAlchemy engine connected through SSH tunnel
            db_uri = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{tunnel.local_bind_port}/{mysql_db}'
            engine = create_engine(db_uri)

            # Create tables and get metadata
            metadata = create_tables(engine)
            print("Tables created successfully.")

            # Print fields in each table
            print_table_fields(metadata)

    except Exception as e:
        print(f"Error creating tables: {e}")

    finally:
        if 'engine' in locals():
            engine.dispose()
        if tunnel:
            tunnel.stop()

if __name__ == "__main__":
    main()