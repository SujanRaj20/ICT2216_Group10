from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
from modules.user_model import User

def anonymous_required(redirect_url='/'):                   # Decorator to redirect to the main page if the user is already logged in
    def decorator(f):                                       # Define a decorator function
        @wraps(f)                                           # Use the wraps decorator to preserve the function metadata
        def decorated_function(*args, **kwargs):            # Define the decorated function
            if current_user.is_authenticated:               # Check if the user is authenticated
                return redirect(url_for(redirect_url))      # Redirect to the main page    
            return f(*args, **kwargs)                       # Call the original function       
        return decorated_function                           # Return the decorated function
    return decorator                                        # Return the decorator  

def admin_required(redirect_url='main.index'):              # Decorator to check if the user is an admin
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

def non_admin_required(redirect_url='main.index'):          # Decorator to check if the user is not an admin
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

def seller_required(redirect_url='main.index'):             # Decorator to check if the user is a seller
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

def buyer_required(redirect_url='main.index'):              # Decorator to check if the user is a buyer
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