import pytest
from flask_app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
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
