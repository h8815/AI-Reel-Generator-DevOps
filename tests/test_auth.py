import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from auth import init_db, create_user, verify_user, hash_password

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    # Use test database
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_home_page(client):
    """Test home page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_register_page_loads(client):
    """Test register page loads"""
    response = client.get('/register')
    assert response.status_code == 200

def test_login_page_loads(client):
    """Test login page loads"""
    response = client.get('/login')
    assert response.status_code == 200

def test_create_requires_login(client):
    """Test create page requires authentication"""
    response = client.get('/create', follow_redirects=False)
    assert response.status_code == 302  # Redirect to login

def test_gallery_requires_login(client):
    """Test gallery page requires authentication"""
    response = client.get('/gallery', follow_redirects=False)
    assert response.status_code == 302  # Redirect to login

def test_password_hashing():
    """Test password hashing works"""
    password = "testpassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) == 64  # SHA-256 produces 64 character hex string

def test_user_registration():
    """Test user can be created"""
    init_db()
    result = create_user("testuser", "test@example.com", "password123")
    assert result == True

def test_user_verification():
    """Test user credentials can be verified"""
    init_db()
    create_user("verifyuser", "verify@example.com", "password123")
    user = verify_user("verifyuser", "password123")
    assert user is not None
    assert user[1] == "verifyuser"

def test_invalid_login():
    """Test invalid credentials fail"""
    init_db()
    user = verify_user("nonexistent", "wrongpassword")
    assert user is None
