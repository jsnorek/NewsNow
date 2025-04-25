from unittest.mock import patch
from app import app
import pytest
from summary import get_summary

# Tests that the get_summary function correctly parses a complete AI summary response
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