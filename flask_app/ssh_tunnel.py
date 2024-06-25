from flask import Flask, render_template,g, jsonify
from jinja2 import TemplateNotFound  # Import the TemplateNotFound exception

import paramiko
from sshtunnel import SSHTunnelForwarder
import pymysql

app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reloading of templates

# Function to create SSH tunnel with PEM key
def create_ssh_tunnel():
    try:
        # SSH server configuration
        ssh_host = '3.145.129.7'
        ssh_port = 22
        ssh_username = 'student25'
        ssh_pem_key = './ICT2216-student25.pem'  # Path to your .pem key file

        # MySQL server configuration
        mysql_host = '172.21.0.2'
        mysql_port = 3306  # Default MySQL port

        # Establish SSH tunnel
        ssh_key = paramiko.RSAKey.from_private_key_file(ssh_pem_key)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ssh_host, port=ssh_port, username=ssh_username, pkey=ssh_key)

        # Create SSH tunnel without passing ssh_client directly
        ssh_tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_pkey=ssh_key,
            remote_bind_address=(mysql_host, mysql_port),
            local_bind_address=('127.0.0.1', 3306)  # local (Flask app) bind address
        )
        ssh_tunnel.start()
        print("SSH tunnel established successfully")
        return ssh_tunnel
    except Exception as e:
        print(f"Error establishing SSH tunnel: {e}")
        return None
    
# Function to get MySQL connection via SSH tunnel
def get_mysql_connection():
    if hasattr(g, 'ssh_tunnel') and g.ssh_tunnel:
        try:
            conn = pymysql.connect(
                host='127.0.0.1',  # local (Flask app) bind address
                port=g.ssh_tunnel.local_bind_port,
                user='root',
                passwd='kMcFNgtzJTA0{XW',
                db='bookwisetesting'
            )
            print("MySQL connection established successfully")
            return conn
        except pymysql.Error as err:
            print(f"MySQL Error: {err}")
            return None
    else:
        print("SSH tunnel not available")
        return None

# Example route that fetches data from MySQL database via SSH tunnel
@app.route('/testdbconn')
def testdbconn():
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM your_table')
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(results), 200
        except pymysql.Error as err:
            print(f"MySQL Error: {err}")
            return jsonify({'error': 'Internal Server Error'}), 500
    else:
        return jsonify({'error': 'Failed to connect to database'}), 500

# Before request hook to create SSH tunnel
@app.before_request
def before_request():
    g.ssh_tunnel = create_ssh_tunnel()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
