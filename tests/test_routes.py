import sys
import os
import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from flask_app.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            pass
        yield client



def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Home' in response.data

def test_signup_page(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

def test_login(client):
    response = client.post('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_protected_route(client):
    response = client.get('/add_admin')
    assert response.status_code == 302
    assert b'Location: /login' in response.headers['Location']
