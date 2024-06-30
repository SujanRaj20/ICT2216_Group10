from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    mail.init_app(app)

  # Flask-Mail configuration for Gmail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'bookwise940@gmail.com'
    app.config['MAIL_PASSWORD'] = 'rtcs mmjk wkit dwnp'  # Use your Gmail App Password here


def send_otp_email(email, otp):
    with mail.connect() as conn:
        msg = Message('Your OTP Code', sender='bookwise940@gmail.com', recipients=[email])
        msg.body = f'Your OTP code is {otp}. Please use this code to complete your login.'
        try:
            conn.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send OTP email: {e}")
            return False
