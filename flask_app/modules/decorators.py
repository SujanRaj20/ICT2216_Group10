from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
from modules.user_model import User

def anonymous_required(redirect_url='/'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(url_for(redirect_url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(redirect_url='main.index'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                user_role = current_user.get_role()
                if user_role != 'admin':
                    return redirect(url_for(redirect_url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def non_admin_required(redirect_url='main.index'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                user_role = current_user.get_role()
                if user_role == 'admin':
                    return redirect(url_for(redirect_url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def seller_required(redirect_url='main.index'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                user_role = current_user.get_role()
                if user_role != 'seller':
                    return redirect(url_for(redirect_url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def buyer_required(redirect_url='main.index'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                user_role = current_user.get_role()
                if user_role != 'buyer':
                    return redirect(url_for(redirect_url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator