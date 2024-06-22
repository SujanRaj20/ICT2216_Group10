from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text

# MySQL Server Parameters
mysql_host = '127.0.0.1'
mysql_port = 3306  # Local port forwarded by SSH tunnel
mysql_user = 'testtoday'
mysql_password = 'kMcFNgtzJTA0{XW'
mysql_db = 'bookwise'

# SSH Tunnel Parameters
ssh_host = '3.145.129.7'
ssh_port = 22
ssh_username = 'student25'
ssh_keyfile = r'C:\Users\Sujan\OneDrive\Desktop\TRI3\ICT2216 - Secure Software Development\ICT2216-student25.pem'


def setup_ssh_tunnel():
    from sshtunnel import SSHTunnelForwarder
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
                  Column('role', String(255), nullable=False),
                  Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                  )

    # Define sessions table
    sessions = Table('sessions', metadata,
                     Column('session_id', Integer, primary_key=True, autoincrement=True),
                     Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
                     Column('status', String(255), nullable=False),
                     Column('session_age', Integer),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    # Define listings table
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

    # Define pictures table
    pictures = Table('pictures', metadata,
                     Column('picture_id', Integer, primary_key=True, autoincrement=True),
                     Column('picture_url', String(255), nullable=False),
                     Column('listing_id', Integer, ForeignKey('listings.listing_id'), nullable=False),
                     Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                     )

    # Define cart table
    cart = Table('cart', metadata,
                 Column('cart_id', Integer, primary_key=True, autoincrement=True),
                 Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
                 Column('itemcount', Integer, nullable=False),
                 Column('totalprice', Integer, nullable=False)
                 )

    # Define items table
    items = Table('items', metadata,
                  Column('item_id', Integer, primary_key=True, autoincrement=True),
                  Column('listing_id', Integer, ForeignKey('listings.listing_id'), nullable=False),
                  Column('cart_id', Integer, ForeignKey('cart.cart_id'))
                  )

    # Define orders table
    orders = Table('orders', metadata,
                   Column('order_id', Integer, primary_key=True, autoincrement=True),
                   Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
                   Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                   )

    # Define transactions table
    transactions = Table('transactions', metadata,
                         Column('transaction_id', Integer, primary_key=True, autoincrement=True),
                         Column('order_id', Integer, ForeignKey('orders.order_id'), nullable=False),
                         Column('status', String(255), nullable=False),
                         Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
                         )

    # Create all tables
    metadata.create_all()

    # Return metadata to access tables later if needed
    return metadata


def print_table_fields(metadata):
    # Print fields in each table
    print("\nFields in Each Table:")
    for table_name in metadata.tables.keys():
        print(f"Table: {table_name}")
        for column in metadata.tables[table_name].c:
            print(f" - {column.name}")


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
