import pytest
from unittest.mock import MagicMock, patch
from sentiment_and_summary import get_sentiment_and_summary

@patch("sentiment_and_summary.client")

# Tests that the get_sentiment_and_summary function returns the correct sentiment and summary from a mocked OpenAI response
def test_get_sentiment_and_summary(mock_client):
    # Mock OpenAI response
    mock_response = MagicMock() # Create a mock object
    mock_response.choices = [MagicMock()] # Simulate a `choices` list with one item
    mock_response.choices[0].message.content = (
        "Summary: This is a test summary.\nSentiment: Positive" # Mocked content returned by the AI
    )
    # Patch the OpenAI API call with this mocked response
    mock_client.chat.completions.create.return_value = mock_response

    # Sample input to the function
    title = "Test Article" # Title of the article
    content = "This is the content of the test article." # Content of the article

    # Call the actual function
    result = get_sentiment_and_summary(title, content)

    # Assert expected output matches the mocked response
    assert result["summary"] == "This is a test summary."
    assert result["sentiment"] == "Positive"
