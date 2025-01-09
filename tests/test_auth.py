import pytest
from flask import Flask
from models import db, User
from auth import auth
from unittest.mock import patch

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    db.init_app(app)
    app.register_blueprint(auth)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def create_test_user(app):
    with app.app_context():
        user = User(email='test@example.com', username='testuser', password='password')
        db.session.add(user)
        db.session.commit()

def test_login_success(client, create_test_user):
    response = client.post('/login', data=dict(username='testuser', password='password'), follow_redirects=True)
    assert b'Logged in successfully!' in response.data

def test_login_failure(client, create_test_user):
    response = client.post('/login', data=dict(username='testuser', password='wrongpassword'), follow_redirects=True)
    assert b'Invalid username or password' in response.data

def test_logout(client, create_test_user):
    with client:
        client.post('/login', data=dict(username='testuser', password='password'), follow_redirects=True)
        response = client.get('/logout', follow_redirects=True)
        assert b'Login' in response.data

@patch('models.User.allergies', new_callable=lambda: ['Peanuts', 'Shellfish'])
def test_sign_up(mock_allergies, client):
    response = client.post('/sign_up', data=dict(
        email='newuser@example.com',
        username='newuser',
        password1='newpassword',
        diet_preferences='Vegan',
        allergies=['Peanuts', 'Shellfish']
    ), follow_redirects=True)
    assert b'Registration successful!' in response.data
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'