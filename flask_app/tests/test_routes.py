import pytest
from flask import url_for
from flask_login import current_user

import pytest
from flask_app.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get(url_for('flask_app.routes.main.index'))
    assert response.status_code == 200
    assert b"Index Page" in response.data

def test_login(client):
    response = client.get(url_for('flask_app.routes.main.login'))
    assert response.status_code == 200
    assert b"Login Page" in response.data

def test_signup(client):
    response = client.get(url_for('flask_app.routes.main.signup'))
    assert response.status_code == 200
    assert b"Signup Page" in response.data

def test_contact(client):
    response = client.get(url_for('flask_app.routes.main.contact'))
    assert response.status_code == 200
    assert b"Contact Page" in response.data

def test_shop(client):
    response = client.get(url_for('flask_app.routes.main.shop'))
    assert response.status_code == 200
    assert b"Shop Page" in response.data

def test_checkout(client):
    response = client.get(url_for('flask_app.routes.main.checkout'))
    assert response.status_code == 200
    assert b"Checkout Page" in response.data

def test_buyeraccount(client):
    response = client.get(url_for('flask_app.routes.main.buyeraccount'))
    assert response.status_code == 200
    assert b"Buyer Account Page" in response.data

def test_seller_signup(client):
    response = client.get(url_for('flask_app.routes.main.seller_signup'))
    assert response.status_code == 200
    assert b"Seller Signup Page" in response.data