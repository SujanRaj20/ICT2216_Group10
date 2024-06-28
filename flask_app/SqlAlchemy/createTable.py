from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os


# MySQL Server Parameters - Local
local_mysql_host = os.getenv('MYSQL_HOST', 'mysql-container')
local_mysql_port = 3306
local_mysql_user = os.getenv('MYSQL_USER', 'bookwise_flask')
local_mysql_password = os.getenv('MYSQL_PASSWORD', '***REMOVED***')
local_mysql_db = os.getenv('MYSQL_DB', '***REMOVED***')

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
                     Column('title', String(255)),
                     Column('body', String(2000)),  # Specify length for VARCHAR
                     Column('rating', Integer),
                     Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                     Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    # Define cart_items table
    cart_items = Table('cart_items', metadata,
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

    metadata.create_all(engine)

    existing_tables = engine.table_names()

    tables_created_or_verified = []

    for table in [users, carts, transactions, listings, pictures, comments, cart_items, orders]:
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
