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

from flask import Flask, render_template
from jinja2 import TemplateNotFound  # Import the TemplateNotFound exception
from routes.main import main_bp  # Import the Blueprint from the routes module
from routes.user import user_bp  # Import the user Blueprint


# Initialize the Flask application
app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reloading of templates

# Register the Blueprint with the app
app.register_blueprint(main_bp)

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 # Display the 404 page whenever a non-existant route is called

# Error handler for TemplateNotFound errors
@app.errorhandler(TemplateNotFound)
def template_not_found(e):
    return render_template('404.html'), 404

# Run the app in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)