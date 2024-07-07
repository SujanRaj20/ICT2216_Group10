import pytest
from flask import url_for
from flask_login import current_user

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            pass
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_signup(client):
    response = client.get('/signup')
    assert response.status_code == 200

def test_contact(client):
    response = client.get('/contact')
    assert response.status_code == 200
    
def test_protected_route(client):
    response = client.get('/add_admin')
    assert response.status_code == 401
