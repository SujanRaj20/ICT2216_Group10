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
    response = client.get(url_for('main.index'))
    assert response.status_code == 200
    assert b"Index Page" in response.data

def test_login(client):
    response = client.get(url_for('main.login'))
    assert response.status_code == 200
    assert b"Login Page" in response.data

def test_signup(client):
    response = client.get(url_for('main.signup'))
    assert response.status_code == 200
    assert b"Signup Page" in response.data

def test_contact(client):
    response = client.get(url_for('main.contact'))
    assert response.status_code == 200
    assert b"Contact Page" in response.data

def test_shop(client):
    response = client.get(url_for('main.shop'))
    assert response.status_code == 200
    assert b"Shop Page" in response.data

def test_checkout(client):
    response = client.get(url_for('main.checkout'))
    assert response.status_code == 200
    assert b"Checkout Page" in response.data

def test_buyeraccount(client):
    response = client.get(url_for('main.buyeraccount'))
    assert response.status_code == 200
    assert b"Buyer Account Page" in response.data

def test_seller_signup(client):
    response = client.get(url_for('main.seller_signup'))
    assert response.status_code == 200
    assert b"Seller Signup Page" in response.data
