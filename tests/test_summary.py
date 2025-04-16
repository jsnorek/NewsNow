from unittest.mock import patch
from app import app
import pytest
from summary import get_summary


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

def test_get_summary_success(monkeypatch):
    class MockMessage:
        content = "Summary: This is a summary."

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    def mock_create(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("summary.client.chat.completions.create", mock_create)

    result = get_summary("Test Title", "Test Content")
    assert result == "This is a summary."

def test_get_summary_incomplete_response(monkeypatch):
    class MockMessage:
        content = "No summary provided."

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    def mock_create(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("summary.client.chat.completions.create", mock_create)

    result = get_summary("Test Title", "Test Content")
    assert result == ""

def test_get_summary_api_failure(monkeypatch):
    def mock_create(*args, **kwargs):
        raise Exception("API call failed")

    monkeypatch.setattr("summary.client.chat.completions.create", mock_create)

    result = get_summary("Test Title", "Test Content")
    assert result == "" 