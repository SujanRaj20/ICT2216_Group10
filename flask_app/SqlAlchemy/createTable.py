import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG


# MySQL Server Parameters - Local
local_mysql_host = os.getenv('MYSQL_HOST', 'mysql-container')
local_mysql_port = 3306
local_mysql_user = os.getenv('MYSQL_USER', 'bookwise_flask')
local_mysql_password = os.getenv('MYSQL_PASSWORD', 'bookwiseflaskpasswordchangelater')
local_mysql_db = os.getenv('MYSQL_DB', 'bookwisetesting')

localengine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')

def create_or_verify_tables(engine):
    metadata = MetaData()

    # Define users table
    users = Table('users', metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('username', String(255), nullable=False, unique=True),
                  Column('password_hash', String(60), nullable=False),
                  Column('fname', String(255), nullable=False),
                  Column('lname', String(255), nullable=False),
                  Column('email', String(255), nullable=False, unique=True),
                  Column('phone_num', String(20)),
                  Column('role', String(20), nullable=False),
                  Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                  )

    # Define carts table
    carts = Table('carts', metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
                  Column('item_count', Integer, nullable=False),
                  Column('total_price', DECIMAL(10, 2), nullable=False),
                  Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                  )

    # Define transactions table
    transactions = Table('transactions', metadata,
                         Column('id', Integer, primary_key=True, autoincrement=True),
                         Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
                         Column('status', String(20), nullable=False),
                         Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                         )

    # Define listings table
    listings = Table('listings', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('title', String(255), nullable=False),
                 Column('description', String(2000)),  # Specify length for VARCHAR
                 Column('keywords', JSON),
                 Column('release_date', DATE),
                 Column('author', String(255)),
                 Column('publisher', String(255)),
                 Column('price', DECIMAL(10, 2), nullable=False),
                 Column('stock', Integer, nullable=False),
                 Column('type', String(20), nullable=False),
                 Column('seller_id', Integer, ForeignKey('users.id'), nullable=False),
                 Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')),
                 Column('imagepath', String(255))
                 )

    # Define pictures table
    pictures = Table('pictures', metadata,
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                     Column('picture_url', String(255), nullable=False),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    # Define comments table
    comments = Table('comments', metadata,
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('title', String(255),nullable=False),
                     Column('body', String(2000), nullable=False),  # Specify length for VARCHAR
                     Column('rating', Integer),
                     Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                     Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    # Define cart_items table
    cart_items = Table('cart_items', metadata,
                       Column('id', Integer, primary_key=True, autoincrement=True),
                       Column('cart_id', Integer, ForeignKey('carts.id'), nullable=False),
                       Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                       Column('quantity', Integer, nullable=False)
                       )

    # Define orders table
    orders = Table('orders', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('transaction_id', Integer, ForeignKey('transactions.id'), nullable=False),
                   Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                   Column('buyer_id', Integer, ForeignKey('users.id'), nullable=False),
                   Column('quantity', Integer, nullable=False)
                   )

     # Define orders table
    wishlist_items = Table('wishlist_items', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                   Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
                   )
    
    reports = Table('reports', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                   Column('buyer_id', Integer, ForeignKey('users.id'), nullable=False),
                   Column('seller_id', Integer, ForeignKey('users.id'), nullable=False),
                   Column('title', String(255),nullable=False),
                   Column('body', String(2000), nullable=False),  # Specify length for VARCHAR
                   Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                   )
    
    comment_reports = Table('comment_reports', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('comment_id', Integer, ForeignKey('comments.id'), nullable=False),
                   Column('reporter_id', Integer, ForeignKey('users.id'), nullable=False),
                   Column('title', String(255),nullable=False),
                   Column('body', String(2000), nullable=False),  # Specify length for VARCHAR
                   Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                   )
    
    metadata.create_all(engine)

    existing_tables = engine.table_names()

    tables_created_or_verified = []

    for table in [users, carts, transactions, listings, pictures, comments, cart_items, orders, wishlist_items, reports, comment_reports]:
        if table.name not in existing_tables:
            table.create(engine)
            tables_created_or_verified.append(f"{table.name} - Table created")
        else:
            # Check if all columns exist in the table
            existing_columns = engine.execute(f"DESCRIBE {table.name}").fetchall()
            expected_columns = [(column.name, str(column.type)) for column in table.columns]
            for column_name, column_type in expected_columns:
                if column_name not in [col[0] for col in existing_columns]:
                    engine.execute(f"ALTER TABLE {table.name} ADD COLUMN {column_name} {column_type}")
                    tables_created_or_verified.append(f"{table.name} - Added column {column_name}")

    return tables_created_or_verified

def print_tables_or_fields_created(tables_or_fields):
    if tables_or_fields:
        print("Tables or Fields Created or Verified:")
        for item in tables_or_fields:
            print(f" - {item}")
    else:
        print("No new tables or fields were created.")
        
# User authentication methods
def get_user_by_id(engine, user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = engine.execute(query).fetchone()
    if result:
        return result
    return None

def get_user_by_username(engine, username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = engine.execute(query).fetchone()
    if result:
        return result
    return None

def authenticate_user(engine, username, password):
    user = get_user_by_username(engine, username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_user_cart_item_count(userid):
    try:
        cart = get_user_cart(userid)
        cart_count = cart['item_count']
        return cart_count
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    
    
def get_wishlist_items(userid):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Get the user's wishlist items
        query = f"""
            SELECT wi.listing_id, l.imagepath, l.title, l.price, wi.id
            FROM wishlist_items wi
            JOIN listings l ON wi.listing_id = l.id
            WHERE wi.user_id = '{userid}'
        """
        wishlist_items = engine.execute(query).fetchall()
        
        return wishlist_items
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    finally:
        engine.dispose()
    
def get_cart_items(userid):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Get the user's cart
        user_cart = get_user_cart(userid)

        cart_id = user_cart['id']
        
        query = f"""
            SELECT ci.listing_id, l.imagepath, l.title, l.price, ci.quantity, ci.id
            FROM cart_items ci
            JOIN listings l ON ci.listing_id = l.id
            WHERE ci.cart_id = '{cart_id}'
        """
        cart_items = engine.execute(query).fetchall()
        
        return cart_items
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    finally:
        engine.dispose()
        
def get_user_cart_value(userid):
    user_cart = get_user_cart(userid)
    cart_value = user_cart['total_price']
    
    return cart_value

def get_user_cart(userid):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        query = f"SELECT * FROM carts WHERE user_id = '{userid}'"
        result = engine.execute(query).fetchone()
        
        # If no cart exists, create a new cart
        if result is None:
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_query = f"""
                    INSERT INTO carts (user_id, item_count, total_price, created_at) 
                    VALUES ('{userid}', 0, 0.0, '{created_at}')
                """
            engine.execute(insert_query)
            # Fetch the newly created cart
            result = engine.execute(query).fetchone()
            
        return result
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    finally:
        engine.dispose()
        
def add_to_cart(user_id, listing_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Get the user's cart
        user_cart = get_user_cart(user_id)

        cart_id = user_cart['id']
        
        # Check if the item already exists in the cart
        check_query = f"""
            SELECT * FROM cart_items 
            WHERE cart_id = '{cart_id}' AND listing_id = '{listing_id}'
        """
        existing_item = engine.execute(check_query).fetchone()
        
        # Get the price of the item from the listing table
        price_query = f"SELECT price FROM listings WHERE id = '{listing_id}'"
        listing = engine.execute(price_query).fetchone()
        if not listing:
            return {'error': 'Listing not found.'}
        
        price = listing['price']
        
        if existing_item:
            # Update the quantity if the item already exists
            new_quantity = existing_item['quantity'] + 1
            update_query = f"""
                UPDATE cart_items 
                SET quantity = '{new_quantity}' 
                WHERE cart_id = '{cart_id}' AND listing_id = '{listing_id}'
            """
            engine.execute(update_query)
        else:
            # Insert a new item if it doesn't exist
            insert_query = f"""
                INSERT INTO cart_items (cart_id, listing_id, quantity) 
                VALUES ('{cart_id}', '{listing_id}', 1)
            """
            engine.execute(insert_query)
            
        # Update the item_count and total_price in the carts table
        new_item_count = user_cart['item_count'] + 1
        new_total_price = user_cart['total_price'] + price
        update_cart_query = f"""
            UPDATE carts 
            SET item_count = '{new_item_count}', total_price = '{new_total_price}'
            WHERE id = '{cart_id}'
        """
        engine.execute(update_cart_query)
            
        return {'message': 'Item added to cart successfully.'}
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return {'error': str(e)}
    finally:
        engine.dispose()
        
def add_to_wishlist(user_id, listing_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
       
        # Check if the item already exists in the cart
        check_query = f"""
            SELECT * FROM wishlist_items 
            WHERE user_id = '{user_id}' AND listing_id = '{listing_id}'
        """
        existing_item = engine.execute(check_query).fetchone()
        
        if not existing_item:
            # Insert a new item if it doesn't exist
            insert_query = f"""
                INSERT INTO wishlist_items (listing_id, user_id) 
                VALUES ('{listing_id}', '{user_id}')
            """
            engine.execute(insert_query)
            
        return {'message': 'Item added to wishlist.'}
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return {'error': str(e)}
    finally:
        engine.dispose()
        
def delete_wishlist_item(wishlist_item_id, user_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    
    try:
        # Delete the cart item
        delete_query = f"""
            DELETE FROM wishlist_items
            WHERE id = '{wishlist_item_id}'
        """
        engine.execute(delete_query)

        return {'success': True}

    except SQLAlchemyError as e:
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()
        
def update_cart_totals(cart_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Calculate the new total price and item count
        total_price_query = f"""
            SELECT SUM(ci.quantity * l.price) as total_price, SUM(ci.quantity) as item_count
            FROM cart_items ci
            JOIN listings l ON ci.listing_id = l.id
            WHERE ci.cart_id = '{cart_id}'
        """
        totals = engine.execute(total_price_query).fetchone()

        total_price = totals['total_price'] if totals['total_price'] else 0
        item_count = totals['item_count'] if totals['item_count'] else 0

        # Update the carts table with the new totals
        update_query = f"""
            UPDATE carts
            SET total_price = '{total_price}', item_count = '{item_count}'
            WHERE id = '{cart_id}'
        """
        engine.execute(update_query)

    except SQLAlchemyError as e:
        print(f"Error updating cart totals: {e}")
    finally:
        engine.dispose()

def increase_cart_item_quantity(cart_item_id, user_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT ci.*, c.id as cart_id, c.user_id FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            WHERE ci.id = '{cart_item_id}' AND c.user_id = '{user_id}'
        """
        cart_item = engine.execute(query).fetchone()
        
        if cart_item:
            # Increase the quantity
            new_quantity = cart_item['quantity'] + 1
            update_query = f"""
                UPDATE cart_items
                SET quantity = '{new_quantity}'
                WHERE id = '{cart_item_id}'
            """
            engine.execute(update_query)

            # Update cart totals
            update_cart_totals(cart_item['cart_id'])

            return {'success': True}
        else:
            return {'success': False, 'error': 'Cart item not found or does not belong to user'}
    except SQLAlchemyError as e:
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()
        
def decrease_cart_item_quantity(cart_item_id, user_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT ci.*, c.id as cart_id, c.user_id FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            WHERE ci.id = '{cart_item_id}' AND c.user_id = '{user_id}'
        """
        cart_item = engine.execute(query).fetchone()
        
        if cart_item:
            if cart_item['quantity'] > 1:
                # Decrease the quantity
                new_quantity = cart_item['quantity'] - 1
                update_query = f"""
                    UPDATE cart_items
                    SET quantity = '{new_quantity}'
                    WHERE id = '{cart_item_id}'
                """
                engine.execute(update_query)
            else:
                # If quantity is 1, delete the item
                delete_query = f"""
                    DELETE FROM cart_items
                    WHERE id = '{cart_item_id}'
                """
                engine.execute(delete_query)

            # Update cart totals
            update_cart_totals(cart_item['cart_id'])

            return {'success': True}
        else:
            return {'success': False, 'error': 'Cart item not found or does not belong to user'}
    except SQLAlchemyError as e:
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()

def delete_cart_item(cart_item_id, user_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    
    try:
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT ci.*, c.id as cart_id, c.user_id FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            WHERE ci.id = '{cart_item_id}' AND c.user_id = '{user_id}'
        """
        cart_item = engine.execute(query).fetchone()
        
        if cart_item:
            # Delete the cart item
            delete_query = f"""
                DELETE FROM cart_items
                WHERE id = '{cart_item_id}'
            """
            engine.execute(delete_query)

            # Update cart totals
            update_cart_totals(cart_item['cart_id'])

            return {'success': True}
        else:
            return {'success': False, 'error': 'Cart item not found or does not belong to user'}
    except SQLAlchemyError as e:
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()
        

def fetch_all_listings_forbuyer(sort_option, category):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    query = f"SELECT * FROM listings"
    
    if category != 'all':
        query += f" WHERE type = '{category}'"
        
    if sort_option == "alpha":
        query += " ORDER BY title ASC"
    elif sort_option == "dateasc":
        query += " ORDER BY created_at ASC"
    elif sort_option == "datedesc":
        query += " ORDER BY created_at DESC"
    elif sort_option == "priceasc":
        query += " ORDER BY price ASC"
    elif sort_option == "pricedesc":
        query += " ORDER BY price DESC"
    elif sort_option == "stockasc":
        query += " ORDER BY stock ASC"
    elif sort_option == "stockdesc":
        query += " ORDER BY stock DESC"
    
    result = engine.execute(query).fetchall()
    engine.dispose()
    return result

def fetch_category_counts_for_shop_buyer():
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    
    # Query to get the count of each category
    category_query = f"""
        SELECT type, COUNT(*) as count
        FROM listings
        GROUP BY type
    """
    category_result = engine.execute(category_query).fetchall()
    category_counts = {row['type']: row['count'] for row in category_result}
    
    # Query to get the total count of listings for the seller
    total_query = f"""
        SELECT COUNT(*) as total_count
        FROM listings
    """
    total_result = engine.execute(total_query).fetchone()
    category_counts['all'] = total_result['total_count']
    
    engine.dispose()
    return category_counts
    

def fetch_seller_listings(seller_id, sort_option, category):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    query = f"SELECT * FROM listings WHERE seller_id = {seller_id}"

    if category != 'all':
        query += f" AND type = '{category}'"

    if sort_option == "alpha":
        query += " ORDER BY title ASC"
    elif sort_option == "dateasc":
        query += " ORDER BY created_at ASC"
    elif sort_option == "datedesc":
        query += " ORDER BY created_at DESC"
    elif sort_option == "priceasc":
        query += " ORDER BY price ASC"
    elif sort_option == "pricedesc":
        query += " ORDER BY price DESC"
    elif sort_option == "stockasc":
        query += " ORDER BY stock ASC"
    elif sort_option == "stockdesc":
        query += " ORDER BY stock DESC"

    result = engine.execute(query).fetchall()
    engine.dispose()
    return result

def fetch_category_counts(seller_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    
    # Query to get the count of each category
    category_query = f"""
        SELECT type, COUNT(*) as count
        FROM listings
        WHERE seller_id = {seller_id}
        GROUP BY type
    """
    category_result = engine.execute(category_query).fetchall()
    category_counts = {row['type']: row['count'] for row in category_result}
    
    # Query to get the total count of listings for the seller
    total_query = f"""
        SELECT COUNT(*) as total_count
        FROM listings
        WHERE seller_id = {seller_id}
    """
    total_result = engine.execute(total_query).fetchone()
    category_counts['all'] = total_result['total_count']
    
    return category_counts

def get_listing_byid(listing_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        query = f"SELECT * FROM listings WHERE id = {listing_id}"
        result = engine.execute(query).fetchone()  # Fetch one instead of fetchall
    except SQLAlchemyError as e:
        logging.error(f"Error fetching listing {listing_id}: {e}")
        result = None
    finally:
        engine.dispose()
    return result

def delete_listing_fromdb(listing_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        query = f"DELETE FROM listings WHERE id = {listing_id}"
        engine.execute(query)
    except SQLAlchemyError as e:
        logging.error(f"Error deleting listing {listing_id}: {e}")
        raise
    finally:
        engine.dispose()
        
def get_seller_info(seller_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    
    try:
        # Query to fetch seller information
        query = f"""
            SELECT username, fname, lname, email, phone_num
            FROM users
            WHERE id = {seller_id}
        """
        
        # Execute the query
        with engine.connect() as connection:
            result = connection.execute(text(query)).fetchone()
        
        if result:
            seller_info = {
                'username': result['username'],
                'fname': result['fname'],
                'lname': result['lname'],
                'email': result['email'],
                'phone_num': result['phone_num']
            }
            return seller_info
        else:
            return None  # Return None if seller_id does not exist
        
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        engine.dispose()
        
        
        
def create_report(title, body, item_id, seller_id, buyer_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    current_app.logger.debug(f"Received in user.py title: {title}, body: {body}, item_id: {item_id}, seller_id: {seller_id}, buyer_id: {buyer_id}")
    
    try:
        # Check if the item already exists in the reports table for this buyer
        check_query = f"""
            SELECT * FROM reports 
            WHERE buyer_id = {buyer_id} AND listing_id = {item_id}
        """
        existing_report = engine.execute(check_query).fetchone()
        
        if not existing_report:
            # Insert a new report if it doesn't exist
            insert_query = f"""
                INSERT INTO reports (title, body, listing_id, buyer_id, seller_id) 
                VALUES ('{title}', '{body}', '{item_id}', '{buyer_id}', '{seller_id}')
            """
            engine.execute(insert_query)
            return {'message': 'Report created successfully.'}
        else:
            return {'message': 'You have already reported this item.'}
    
    except SQLAlchemyError as e:
        error_message = f"SQLAlchemy Error: {e}"
        current_app.logger.error(error_message)
        return {'error': error_message}
    except Exception as e:
        error_message = f"Error: {e}"
        current_app.logger.error(error_message)
        return {'error': error_message}
    finally:
        engine.dispose()


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']
        self.fname = user_data['fname']
        self.lname = user_data['lname']
        self.email = user_data['email']
        self.phone_num = user_data['phone_num']
        self.role = user_data['role']
        
    def get_role(self):
        return self.role

    @staticmethod
    def get(user_id):
        engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
        user_data = get_user_by_id(engine, user_id)
        engine.dispose()
        if user_data:
            return User(user_data)
        return None
    


def main():
    try:
        local_db_uri = f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}'
        local_engine = create_engine(local_db_uri)
        tables_or_fields = create_or_verify_tables(local_engine)
        print_tables_or_fields_created(tables_or_fields)
        print("Tables created or verified successfully for local MySQL.")
        print("\nFields in Each Table:")
        for table in local_engine.table_names():
            print(f"Table: {table}")
            for column in local_engine.execute(f"DESCRIBE {table}"):
                print(f" - {column['Field']} ({column['Type']})")

    except Exception as e:
        print(f"Error creating tables: {e}")

    finally:
        if 'local_engine' in locals():
            local_engine.dispose()
            
    return 0

if __name__ == "__main__":
    main()
        
def create_comment(title, body, rating, item_id, user_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Insert the new comment into the comments table
        insert_query = f"""
                INSERT INTO comments (title, body, rating, listing_id, user_id) 
                VALUES ('{title}', '{body}', '{rating}', '{item_id}', '{user_id}')
            """
            
            
        engine.execute(insert_query)
        
        return {'message': 'Comment created successfully.'}
    
    except SQLAlchemyError as e:
        current_app.logger.error(f"SQLAlchemy Error: {e}")
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return {'error': str(e)}
    finally:
        engine.dispose()
        
        
def get_comments_for_item(item_id):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        # Get the user's wishlist items
        query = f"""
            SELECT c.title, c.body, c.rating, c.created_at, u.username, u.fname, u.lname
            FROM comments c
            JOIN users u ON c.user_id = c.id
            WHERE c.listing_id = '{item_id}'
        """
        
        current_app.logged.debug(query)
        
        comments = engine.execute(query).fetchall()
        
        return comments
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    finally:
        engine.dispose()
        
def create_comment_report(comment_id, reporter_id, title, body):
    engine = create_engine(f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}')
    try:
        insert_query = """
            INSERT INTO comment_reports (comment_id, reporter_id, title, body) 
            VALUES (%s, %s, %s, %s)
        """
        with engine.connect() as conn:
            conn.execute(insert_query, (comment_id, reporter_id, title, body))
        return {'message': 'Report created successfully.'}
    except SQLAlchemyError as e:
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        return {'error': str(e)}
    finally:
        engine.dispose()