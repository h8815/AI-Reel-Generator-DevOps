import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Create Stunning Reels in Minutes" in response.data

def test_create_requires_login(client):
    """Test that the create reel page requires authentication (redirects to login)."""
    response = client.get('/create', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_gallery_requires_login(client):
    """Test that the gallery page requires authentication (redirects to login)."""
    response = client.get('/gallery', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_create_reel_no_session_redirects(client):
    """Test that posting to /create without a session redirects to login."""
    response = client.post('/create', data={}, follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_register_page_loads(client):
    """Test that the register page loads."""
    response = client.get('/register')
    assert response.status_code == 200

def test_login_page_loads(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200