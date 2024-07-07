import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime
import os

from modules.db_engine import get_engine # custom function imported from another file to get db engine

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG


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
                Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                Column('item_count', Integer, nullable=False),
                Column('total_price', DECIMAL(10, 2), nullable=False),
                Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                )

    # Define transactions table
    transactions = Table('transactions', metadata,
                        Column('id', Integer, primary_key=True, autoincrement=True),
                        Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
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
                    Column('sales', Integer, nullable=False),
                    Column('stock', Integer, nullable=False),
                    Column('type', String(20), nullable=False),
                    Column('seller_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')),
                    Column('imagepath', String(255))
                    )

    # Define pictures table
    pictures = Table('pictures', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('listing_id', Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False),
                    Column('picture_url', String(255), nullable=False),
                    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                    )

    # Define comments table
    comments = Table('comments', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('title', String(255), nullable=False),
                    Column('body', String(2000), nullable=False),  # Specify length for VARCHAR
                    Column('rating', Integer),
                    Column('listing_id', Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False),
                    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                    )

    # Define cart_items table
    cart_items = Table('cart_items', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('cart_id', Integer, ForeignKey('carts.id', ondelete='CASCADE'), nullable=False),
                    Column('listing_id', Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False),
                    Column('quantity', Integer, nullable=False)
                    )

    # Define orders table
    orders = Table('orders', metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('transaction_id', Integer, ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False),
                Column('keywords', JSON),
                Column('total_price', DECIMAL(10, 2), nullable=False),
                Column('buyer_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                Column('quantity', Integer, nullable=False)
                )

    # Define wishlist_items table
    wishlist_items = Table('wishlist_items', metadata,
                        Column('id', Integer, primary_key=True, autoincrement=True),
                        Column('listing_id', Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False),
                        Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
                        )

    # Define reports table
    reports = Table('reports', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('listing_id', Integer, ForeignKey('listings.id', ondelete='CASCADE'), nullable=False),
                    Column('buyer_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                    Column('seller_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                    Column('title', String(255), nullable=False),
                    Column('body', String(2000), nullable=False),  # Specify length for VARCHAR
                    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                    )

    # Define comment_reports table
    comment_reports = Table('comment_reports', metadata,
                            Column('id', Integer, primary_key=True, autoincrement=True),
                            Column('comment_id', Integer, ForeignKey('comments.id', ondelete='CASCADE'), nullable=False),
                            Column('reporter_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                            Column('title', String(255), nullable=False),
                            Column('body', String(2000), nullable=False),  # Specify length for VARCHAR
                            Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                            )
    
    metadata.create_all(engine)

    
    existing_tables = engine.table_names()

    tables_created_or_verified = []

    for table in [users, carts, transactions, listings, pictures, comments, cart_items, orders, wishlist_items, reports, comment_reports]:
        if table.name not in existing_tables:                                   # iterates over the list of tables to check if it already exists
            table.create(engine)                                                # if it doesnt already exist, it is created
            tables_created_or_verified.append(f"{table.name} - Table created")  # once created, it is added to the list of tables created or verified to already exist 
        else:
            # Check if all columns exist in the table
            existing_columns = engine.execute(f"DESCRIBE {table.name}").fetchall()              #if a tables does already exists, all the columns from it are fetched
            expected_columns = [(column.name, str(column.type)) for column in table.columns]    #the list of columns fetched is compared 
            for column_name, column_type in expected_columns:                                   #to the list of columns it should have
                if column_name not in [col[0] for col in existing_columns]:                     #if the column doesnt exist, it is created
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

def main():
    try:
        local_engine = get_engine()
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
        

    
        
