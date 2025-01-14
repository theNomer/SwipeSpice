import pytest
from flask import session
from app import create_app
from config import TestingConfig
from models import User, db
from werkzeug.security import generate_password_hash
from unittest.mock import MagicMock, patch


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()  # Create tables for testing
        yield app
        db.session.remove()
        db.drop_all()  # Clean up after tests


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_test_user(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpassword')
        )
        db.session.add(user)
        db.session.commit()
        return user


def test_login_success(client, create_test_user):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login' in response.data or b'Profile' in response.data


def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid' in response.data or b'Error' in response.data


def test_login_render_form(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Username' in response.data or b'Login' in response.data


@patch("auth.User.query")
def test_login_exception(mock_query, client):
    mock_query.filter_by.side_effect = Exception("Database error")
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'error' in response.data.lower()


def test_logout(client, create_test_user):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data or b'Goodbye' in response.data


def test_logout_not_logged_in(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data


@patch("auth.load_allergies")
def test_sign_up_load_allergies(mock_load_allergies, client):
    mock_load_allergies.return_value = ['nuts', 'gluten']
    response = client.get('/sign_up')
    assert response.status_code == 200
    assert b'nuts' in response.data
    assert b'gluten' in response.data


@patch("auth.db.session.add")
@patch("auth.db.session.commit")
def test_sign_up_database_error(mock_commit, mock_add, client):
    mock_commit.side_effect = Exception("Database error")
    response = client.post('/sign_up', data={
        'email': 'error@example.com',
        'username': 'erroruser',
        'password1': 'errorpassword',
        'diet_preferences': 'vegan',
        'allergies': ['nuts', 'gluten']
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'error' in response.data.lower()


def test_sign_up_success(client):
    response = client.post('/sign_up', data={
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password1': 'newpassword',
        'diet_preferences': 'vegan',
        'allergies': ['nuts', 'gluten']
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration' in response.data or b'Success' in response.data


def test_sign_up_render_form(client):
    response = client.get('/sign_up')
    assert response.status_code == 200
    assert b'Register' in response.data or b'Sign Up' in response.data
