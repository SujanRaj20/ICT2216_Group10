from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/img/<filename>')
def send_image(filename):
    return send_from_directory('static/img', filename)

if __name__ == "__main__":
    app.run(debug=True)
