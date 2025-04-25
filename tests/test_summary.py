from unittest.mock import patch
from app import app
import pytest
from summary import get_summary

# Tests that the get_summary function correctly parses a complete AI summary response
def test_get_summary_success(monkeypatch):
    
    # Mock the structure of OpenAI's response
    class MockMessage:
        content = "Summary: This is a summary." # The expected content of the AI's message

    class MockChoice:
        message = MockMessage() # Attach the mock message to the "choice"

    class MockResponse:
        choices = [MockChoice()] # Mock AI response with a single choice

    # Monkeypatch OpenAI API call to return the mock response
    def mock_create(*args, **kwargs):
        return MockResponse()

    # Use monkeypatch to simulate the AI API's behavior without making a real API call
    monkeypatch.setattr("summary.client.chat.completions.create", mock_create)

    # Call the summary function and assert expected output
    result = get_summary("Test Title", "Test Content") # Test title and content
    assert result == "This is a summary." # Ensure the returned summary matches the mock content

# Test that the get_summary function handles incomplete responses
def test_get_summary_incomplete_response(monkeypatch):
    
    # Simulate an AI message without a valid summary by defining mock response
    class MockMessage:
        content = "No summary provided." # Simulate an incomplete or invalid response

    class MockChoice:
        message = MockMessage() # Attach the mock message to the "choice"

    class MockResponse:
        choices = [MockChoice()] # Mock AI response with a single choice

    # Define a mock `create` function that returns the mock response when called
    def mock_create(*args, **kwargs):
        return MockResponse()

    # Use monkeypatch to replace the actual `create` method with the mock version
    monkeypatch.setattr("summary.client.chat.completions.create", mock_create)

    # Call `get_summary` with test inputs and check the result
    result = get_summary("Test Title", "Test Content")
    assert result == "" # Ensure the result is empty for an incomplete response

# Test that the `get_summary` function handles API failures properly
def test_get_summary_api_failure(monkeypatch):
    def mock_create(*args, **kwargs):
        raise Exception("API call failed")

    monkeypatch.setattr("summary.client.chat.completions.create", mock_create)

    result = get_summary("Test Title", "Test Content")
    assert result == "" 