from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sshtunnel import SSHTunnelForwarder

# MySQL Server Parameters - Local
local_mysql_host = '172.18.0.2'
local_mysql_port = 3306
local_mysql_user = 'root'
local_mysql_password = 'kMcFNgtzJTA0{XW'
local_mysql_db = 'bookwisetesting'

# MySQL Server Parameters - VM via SSH
ssh_host = '3.145.129.7'
ssh_port = 22
ssh_user = 'student25'
ssh_pkey = r'C:\Users\Sujan\OneDrive\Desktop\TRI3\ICT2216 - Secure Software Development\ICT2216-student25.pem'
vm_mysql_host = '172.21.0.2'
vm_mysql_port = 3306
vm_mysql_user = 'sqlAlchemy'
vm_mysql_password = 'kMcFNgtzJTA0{XW'
vm_mysql_db = 'bookwisetesting'

def setup_ssh_tunnel(ssh_host, ssh_port, ssh_user, ssh_pkey, remote_bind_address):
    try:
        tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=ssh_pkey,
            remote_bind_address=remote_bind_address,
        )
        tunnel.start()
        print(f"SSH tunnel established on local port {tunnel.local_bind_port}")
        return tunnel
    except Exception as e:
        print(f"Error establishing SSH tunnel: {e}")
        return None

def create_tables(engine):
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
    users.create(engine)  # Ensure users table is created first

    # Define carts table
    carts = Table('carts', metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
                  Column('item_count', Integer, nullable=False),
                  Column('total_price', DECIMAL(10, 2), nullable=False),
                  Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                  )
    carts.create(engine)

    # Define transactions table
    transactions = Table('transactions', metadata,
                         Column('id', Integer, primary_key=True, autoincrement=True),
                         Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
                         Column('status', String(20), nullable=False),
                         Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                         )
    transactions.create(engine)

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
    listings.create(engine)

    # Define pictures table
    pictures = Table('pictures', metadata,
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                     Column('picture_url', String(255), nullable=False),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )
    pictures.create(engine)

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
    comments.create(engine)

    # Define cart_items table
    cart_items = Table('cart_items', metadata,
                       Column('cart_id', Integer, ForeignKey('carts.id'), nullable=False),
                       Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                       Column('quantity', Integer, nullable=False)
                       )
    cart_items.create(engine)

    # Define orders table
    orders = Table('orders', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('transaction_id', Integer, ForeignKey('transactions.id'), nullable=False),
                   Column('listing_id', Integer, ForeignKey('listings.id'), nullable=False),
                   Column('buyer_id', Integer, ForeignKey('users.id'), nullable=False),
                   Column('quantity', Integer, nullable=False)
                   )
    orders.create(engine)

    return metadata

def print_table_fields(metadata):
    print("\nFields in Each Table:")
    for table in metadata.sorted_tables:
        print(f"Table: {table.name}")
        for column in table.columns:
            print(f" - {column.name} ({column.type})")

def main():
    try:
        # Set up SSH tunnel for VM
        vm_tunnel = setup_ssh_tunnel(ssh_host, ssh_port, ssh_user, ssh_pkey, (vm_mysql_host, vm_mysql_port))

        if vm_tunnel:
            # Create SQLAlchemy engine connected through SSH tunnel for VM
            vm_db_uri = f'mysql+pymysql://{vm_mysql_user}:{vm_mysql_password}@127.0.0.1:{vm_tunnel.local_bind_port}/{vm_mysql_db}'
            vm_engine = create_engine(vm_db_uri)
            vm_metadata = create_tables(vm_engine)
            print("Tables created successfully for VM.")

            # Print fields in tables for VM
            print_table_fields(vm_metadata)

        # Commented out local MySQL connection to avoid timeout error
        # local_db_uri = f'mysql+pymysql://{local_mysql_user}:{local_mysql_password}@{local_mysql_host}:{local_mysql_port}/{local_mysql_db}'
        # local_engine = create_engine(local_db_uri)
        # local_metadata = create_tables(local_engine)
        # print("Tables created successfully for local MySQL.")

        # Print fields in tables for local MySQL
        # print_table_fields(local_metadata)

    except Exception as e:
        print(f"Error creating tables: {e}")

    finally:
        if 'vm_engine' in locals():
            vm_engine.dispose()
        if vm_tunnel:
            vm_tunnel.stop()
        # if 'local_engine' in locals():
        #     local_engine.dispose()

if __name__ == "__main__":
    main()
