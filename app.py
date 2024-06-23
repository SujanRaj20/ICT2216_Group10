# from flask import Flask, render_template, send_from_directory

# app = Flask(__name__, static_url_path='/static')
# app.config['TEMPLATES_AUTO_RELOAD'] = True


# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route('/img/<filename>')
# def send_image(filename):
#     return send_from_directory('static/img', filename)

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask
from routes.main import main_bp  # Import the Blueprint from the routes module
from routes.user import user_bp  # Import the user Blueprint


# Initialize the Flask application
app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reloading of templates

# Register the Blueprint with the app
app.register_blueprint(main_bp)

# Run the app in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)