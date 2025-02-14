import pytest
from models import NewsArticle

def test_add_article(test_session):
    # Create a new NewsArticle object with test data
    article = NewsArticle(headline="Test Headline", summary="Test Summary", link="http://test.com")
    
    # Add the new article to the session
    test_session.add(article)
    
    # Commit the changes to the database
    test_session.commit()
    
    # Query the database for the article with the specified headline
    fetched_article = test_session.query(NewsArticle).filter_by(headline="Test Headline").first()
    
    # Assert that the article was successfully added and fetched
    assert fetched_article is not None
    assert fetched_article.link == "http://test.com"

def test_edit_article(test_session):
    # Create a new NewsArticle object with initial test data
    article = NewsArticle(headline="Old Headline", summary="Old Summary", link="http://old.com")
    
    # Add the new article to the session
    test_session.add(article)
    
    # Commit the changes to the database
    test_session.commit()

    # Update the headline of the existing article
    article.headline = "New Headline"
    
    # Commit the changes to the database
    test_session.commit()

    # Query the database for the article with the updated headline
    updated_article = test_session.query(NewsArticle).filter_by(headline="New Headline").first()
    
    # Assert that the article was successfully updated
    assert updated_article is not None

def test_delete_article(test_session):
    # Create a new NewsArticle object with test data to delete
    article = NewsArticle(headline="To Delete", summary="Summary", link="http://delete.com")
    
    # Add the new article to the session
    test_session.add(article)
    
    # Commit the changes to the database
    test_session.commit()

    # Delete the article from the session
    test_session.delete(article)
    
    # Commit the changes to the database
    test_session.commit()

    # Query the database to ensure the article has been deleted
    deleted_article = test_session.query(NewsArticle).filter_by(headline="To Delete").first()
    
    # Assert that the article was successfully deleted
    assert deleted_article is None
