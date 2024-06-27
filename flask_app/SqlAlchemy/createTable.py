from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os


# MySQL Server Parameters - Local
local_mysql_host = os.getenv('MYSQL_HOST', 'mysql-container')
local_mysql_port = 3306
local_mysql_user = os.getenv('MYSQL_USER', 'bookwise_flask')
local_mysql_password = os.getenv('MYSQL_PASSWORD', 'bookwiseflaskpasswordchangelater')
local_mysql_db = os.getenv('MYSQL_DB', 'bookwisetesting')

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
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
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