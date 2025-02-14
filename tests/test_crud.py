import pytest
from flask import url_for
from app import app, session
from models import NewsArticle

@pytest.fixture
def client():
    """Creates a test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_article():
    """Creates a test article in the database."""
    article = NewsArticle(headline="Test Article", summary="Test summary", link="http://example.com/test")
    session.add(article)
    session.commit()
    yield article
    session.delete(article)
    session.commit()

def test_index_page(client):
    """Test if the homepage loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "News Articles" in response.get_data(as_text=True)

def test_add_article(client):
    """Test adding a new article."""
    response = client.post("/add", data={"headline": "New Article", "summary": "Summary", "link": "http://example.com"})
    assert response.status_code == 302  # Should redirect
    assert session.query(NewsArticle).filter_by(headline="New Article").first() is not None

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