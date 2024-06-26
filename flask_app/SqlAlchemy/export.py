from sqlalchemy import create_engine, MetaData
from sshtunnel import SSHTunnelForwarder
import os

# SSH and MySQL Server Parameters
ssh_host = '3.145.129.7'
ssh_port = 22
ssh_user = 'student25'
ssh_pkey = r'C:\Users\Sujan\OneDrive\Desktop\TRI3\ICT2216 - Secure Software Development\ICT2216-student25.pem'
mysql_host = '172.21.0.2'
mysql_port = 3306  # Default MySQL port
mysql_user = 'sqlAlchemy'
mysql_password = '***REMOVED***'  # Replace with your actual password
mysql_db = '***REMOVED***'

# Folder to export schema files
export_folder = r'C:\Users\Sujan\OneDrive\Desktop\export'

def setup_ssh_tunnel():
    try:
        tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=ssh_pkey,
            remote_bind_address=(mysql_host, mysql_port),
        )
        tunnel.start()
        print(f"SSH tunnel established on local port {tunnel.local_bind_port}")
        return tunnel
    except Exception as e:
        print(f"Error establishing SSH tunnel: {e}")
        return None

# Set up SSH tunnel
ssh_tunnel = setup_ssh_tunnel()
if not ssh_tunnel:
    exit()

try:
    # Create SQLAlchemy engine connected through SSH tunnel
    db_uri = f'mysql+pymysql://{mysql_user}:{mysql_password}@127.0.0.1:{ssh_tunnel.local_bind_port}/{mysql_db}'
    engine = create_engine(db_uri)

    # Reflect metadata to get list of tables
    metadata = MetaData(bind=engine)
    metadata.reflect()

    print("Connected to MySQL server via SSH tunnel.")
    
    # Print list of tables
    print("\nList of Tables:")
    for table_name in metadata.tables.keys():
        print(f" - {table_name}")

    # Export schema to files
    for table in metadata.sorted_tables:
        schema_file = os.path.join(export_folder, f"{table.name}_schema.sql")
        with open(schema_file, 'w') as f:
            # Generate CREATE TABLE statement
            f.write(f"CREATE TABLE {table.name} (\n")
            for column in table.columns:
                f.write(f"    {column.compile(dialect=engine.dialect)}")
                if column.comment:
                    f.write(f" COMMENT '{column.comment}'")
                f.write(",\n")
            for constraint in table.constraints:
                if constraint.__class__.__name__ == 'PrimaryKeyConstraint':
                    f.write(f"    PRIMARY KEY ({', '.join(column.name for column in constraint.columns)}),\n")
                else:
                    f.write(f"    {constraint}\n")
            f.write(");\n\n")
        print(f"Exported schema for table '{table.name}' to {schema_file}")

except Exception as e:
    print(f"Error connecting to MySQL via SSH tunnel: {e}")

finally:
    ssh_tunnel.stop()