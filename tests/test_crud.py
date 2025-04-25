from unittest.mock import patch
import pytest
from flask import url_for
from app import app, session
from models import NewsArticle, create_or_open_index
from whoosh.writing import AsyncWriter

@pytest.fixture
def client():
    """Creates a test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_article():
    """Creates and indexes a test article in the database and Whoosh index."""
    article = NewsArticle(
        headline="Test Article",
        summary="Test summary for search",
        link="http://example.com/test",
    )
    session.add(article)
    session.commit()

    # Index the article in Whoosh
    ix = create_or_open_index()
    writer = AsyncWriter(ix)
    writer.add_document(
        id=str(article.id),
        headline=article.headline,
        summary=article.summary,
    )
    writer.commit()

    yield article

    # Teardown: remove article from DB and optionally reindex
    session.delete(article)
    session.commit()

# -------------------- Page & CRUD Tests --------------------

def test_index_page(client):
    """Test if the homepage loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "News Articles" in response.get_data(as_text=True)

def test_add_article(client):
    """Test adding a new article."""
    response = client.post("/add", data={"headline": "New Article", "summary": "Summary", "link": "http://example.com"})
    assert response.status_code == 302  # Should redirect
    added = session.query(NewsArticle).filter_by(headline="New Article").first()
    assert added is not None
    session.delete(added)
    session.commit()

def test_edit_article(client, test_article):
    """Test editing an article."""
    response = client.post(f"/edit/{test_article.id}", data={"headline": "Updated", "summary": "Updated summary", "link": test_article.link})
    assert response.status_code == 302
    updated_article = session.query(NewsArticle).get(test_article.id)
    assert updated_article.headline == "Updated"

def test_delete_article(client, test_article):
    """Test deleting an article."""
    response = client.post(f"/delete/{test_article.id}")
    assert response.status_code == 302
    assert session.query(NewsArticle).get(test_article.id) is None

# -------------------- Weather Update Test --------------------

def test_update_weather(client):
    response = client.post('/update_weather', follow_redirects=True)
    assert response.status_code == 200
    assert b"Weather updated successfully!" in response.data or b"Failed to update weather data" in response.data

# -------------------- Search Function Tests --------------------

def test_search_function_valid_query(client, test_article):
    """Test search with a valid query."""
    response = client.get(f"/search?query=Test")
    html = response.get_data(as_text=True)
    assert "Test Article" in html

def test_search_function_no_results(client):
    """Test search with no matching results."""
    response = client.get("/search?query=NoMatch")
    html = response.get_data(as_text=True)
    assert "No articles found for your search." in html  # Ensure flash message appears

def test_search_function_empty_query(client):
    """Test search with an empty query."""
    response = client.get("/search?query=")
    html = response.get_data(as_text=True)
    assert "Please enter a search term." in html  # Ensure warning appears

# -------------------- AI Summary Tests --------------------

# Test successful summary generation via the /api/summary route
def test_summary_success(client):
    mock_summary = "This is a mock summary." # Define a mock summary to return from the AI function

    # Patch the get_summary function to return the mock_summary instead of calling the real AI
    with patch("app.get_summary", return_value=mock_summary):
        # Simulate a POST request to the /api/summary endpoint with article data
        response = client.post("/api/summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })
        
        data = response.get_json() # Parse the reponse JSON
        assert response.status_code == 200 # Assert the request was successful
        assert data["summary"] == mock_summary # Assert the summary matches the mock

# Test when the AI returns an incomplete response (None), triggering a 500 error
def test_summary_incomplete_response(client):
    # Patch get_summary to simulate an incomplete AI response (None)
    with patch("app.get_summary", return_value=None):
        # Simulate a POST request to the endpoint
        response = client.post("/api/summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })

        data = response.get_json() # Parse the response JSON
        assert response.status_code == 500 # Should return internal server error
        assert "error" in data # Confirm that an error message exists
        assert data["error"] == "Incomplete AI response" # Check for specific error message

# Test unexpected internal error during AI summary generation that raises exception
def test_summary_internal_error(client):
    # Patch get_summary to raise an exception when called
    with patch("app.get_summary", side_effect=Exception("Something went wrong")):
        # Simulate the POST request
        response = client.post("/api/summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })
        
        assert response.status_code == 500 # Expect internal server error
        data = response.get_json() # Parse JSON response
        assert "error" in data # Ensure error message is present

# -------------------- AI Sentiment and Summary Tests --------------------

# Test success case for sentiment + summary with DB update
def test_sentiment_and_summary_success(client):
    # Define a mock result to return from the AI function
    mock_result = {
        "summary": "This is a mock AI summary.",
        "sentiment": "Positive"
    }

    # Create a mock article in the test DB to be updated
    article = NewsArticle(
        headline="Test Title",
        summary="Original Summary",
        link="http://example.com"
    )
    session.add(article)
    session.commit() # Commit the article so it exists in the DB

    # Patch the AI function to return the mock sentiment + summary
    with patch("app.get_sentiment_and_summary", return_value=mock_result):
        # Send POST request to the endpoint
        response = client.post("/api/sentiment-and-summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })

        data = response.get_json() # Parse the response
        assert response.status_code == 200 # Expect request success
        assert data["sentiment"] == mock_result["sentiment"] # Check returned sentiment
        assert data["ai_summary"] == mock_result["summary"] # Check returned summary

        # Query the DB to confirm it was updated
        updated_article = session.query(NewsArticle).filter_by(headline="Test Title").first()
        assert updated_article.sentiment == mock_result["sentiment"] # Check the updated article's sentiment 
        assert updated_article.ai_summary == mock_result["summary"] # Check the updated article's summary

# Test unexpected error during AI sentiment + summary generation
def test_sentiment_and_summary_unexpected_error(client):
    # Patch to simulate an exception from the AI function
    with patch("app.get_sentiment_and_summary", side_effect=Exception("Something went wrong")):
        # Provide mock JSON data simulating an article with a title and content
        response = client.post("/api/sentiment-and-summary", json={
            "title": "Test Title",
            "content": "Test content of the article."
        })

        assert response.status_code == 500 # Expect internal server error
        data = response.get_json() # Parse the response
        assert "error" in data # Ensure error field exists in response

# Test case for AI sentiment + summary generation when the article is not found in the DB
def test_sentiment_and_summary_article_not_found(client):
    mock_result = {
        "sentiment": "Positive",
        "summary": "This is a mock AI summary."
    }
    with patch("app.get_sentiment_and_summary", return_value=mock_result):
        response = client.post("/api/sentiment-and-summary", json={
            "title": "Nonexistent Article",
            "content": "Some content"
        })

        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "Article not found"

def test_sentiment_and_summary_incomplete_ai_response(client):
    mock_result = {
        "summary": "Partial summary.",
        "sentiment": None
    }

    article = NewsArticle(
        headline="Test Title",
        summary="Original summary",
        link="http://example.com"
    )
    session.add(article)
    session.commit()

    with patch("app.get_sentiment_and_summary", return_value=mock_result):
        response = client.post("/api/sentiment-and-summary", json={
            "title": "Test Title",
            "content": "Test content"
        })

        data = response.get_json()
        assert response.status_code == 500
        assert data["error"] == "Incomplete AI response"