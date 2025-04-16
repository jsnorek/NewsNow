from unittest.mock import patch
from app import app
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_summary_success(client):
    mock_summary = "This is a mock summary."

    with patch("app.get_summary", return_value=mock_summary):
        response = client.post("/api/summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })
        
        data = response.get_json()
        assert response.status_code == 200
        assert data["summary"] == mock_summary

def test_summary_incomplete_response(client):
    with patch("app.get_summary", return_value=None):
        response = client.post("/api/summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })

        data = response.get_json()
        assert response.status_code == 500
        assert "error" in data
        assert data["error"] == "Incomplete AI response"

def test_summary_internal_error(client):
    with patch("app.get_summary", side_effect=Exception("Something went wrong")):
        response = client.post("/api/summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data