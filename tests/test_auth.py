import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import auth

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Point DATABASE at a fresh temp file for every test, then clean up."""
    db_file = str(tmp_path / 'test_users.db')
    monkeypatch.setattr(auth, 'DATABASE', db_file)
    auth.init_db()
    yield
    # tmp_path is cleaned up automatically by pytest

@pytest.fixture
def client():
    from main import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

# ── Page load tests ──────────────────────────────────────────────────────────

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
    assert response.status_code == 302

def test_gallery_requires_login(client):
    """Test gallery page requires authentication"""
    response = client.get('/gallery', follow_redirects=False)
    assert response.status_code == 302

# ── Password / auth unit tests ────────────────────────────────────────────────

def test_password_hashing():
    """Test password hashing produces a non-plaintext value"""
    from auth import hash_password, check_password_hash
    from werkzeug.security import check_password_hash
    password = "testpassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert check_password_hash(hashed, password)

def test_user_registration():
    """Test user can be created"""
    result = auth.create_user("testuser", "test@example.com", "password123")
    assert result is True

def test_duplicate_user_registration():
    """Test duplicate username is rejected"""
    auth.create_user("dupeuser", "dupe@example.com", "password123")
    result = auth.create_user("dupeuser", "other@example.com", "password456")
    assert result is False

def test_user_verification():
    """Test user credentials can be verified"""
    auth.create_user("verifyuser", "verify@example.com", "password123")
    user = auth.verify_user("verifyuser", "password123")
    assert user is not None
    assert user[1] == "verifyuser"

def test_invalid_login():
    """Test invalid credentials fail"""
    user = auth.verify_user("nonexistent", "wrongpassword")
    assert user is None

def test_wrong_password_fails():
    """Test correct username but wrong password returns None"""
    auth.create_user("wrongpw", "wrongpw@example.com", "correctpassword")
    user = auth.verify_user("wrongpw", "wrongpassword")
    assert user is None
