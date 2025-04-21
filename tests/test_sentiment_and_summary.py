import pytest
from unittest.mock import MagicMock, patch
from sentiment_and_summary import get_sentiment_and_summary

@patch("sentiment_and_summary.client")
def test_get_sentiment_and_summary(mock_client):
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        "Summary: This is a test summary.\nSentiment: Positive"
    )
    mock_client.chat.completions.create.return_value = mock_response

    # Sample input
    title = "Test Article"
    content = "This is the content of the test article."

    # Call the function
    result = get_sentiment_and_summary(title, content)

    # Assert expected output
    assert result["summary"] == "This is a test summary."
    assert result["sentiment"] == "Positive"
