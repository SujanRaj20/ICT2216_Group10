from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    mail.init_app(app)

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'mail.smtp2go.com'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = '2200975@sit.singaporetech.edu.sg'
    app.config['MAIL_PASSWORD'] = 'cDoQYM9F624qF5mI'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

def send_otp_email(email, otp):
    with mail.connect() as conn:
        msg = Message('Your OTP Code', sender='2200975@sit.singaporetech.edu.sg', recipients=[email])
        msg.body = f'Your OTP code is {otp}. Please use this code to complete your login.'
        try:
            conn.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send OTP email: {e}")
            return False
