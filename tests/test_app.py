import pytest
from main import app
from flask import url_for
import os

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Create Stunning Reels in Minutes" in response.data

def test_create_page(client):
    """Test that the create reel page loads successfully."""
    response = client.get('/create')
    assert response.status_code == 200
    assert b"Create Your Reel" in response.data

def test_gallery_page(client):
    """Test that the gallery page loads successfully."""
    response = client.get('/gallery')
    assert response.status_code == 200
    assert b"Reel Gallery" in response.data

# You can add more complex tests here, for example, to test file uploads and reel creation.
# This would involve mocking the file uploads and the subprocess call to FFmpeg.
# For example, you could test the `create` route's validation logic: 

def test_create_reel_no_name(client):
    """Test that creating a reel without a name returns an error."""
    data = {}
    response = client.post('/create', data=data)
    assert response.status_code == 200
    assert b"Please provide a name for your reel." in response.data