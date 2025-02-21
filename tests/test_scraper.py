import pytest
from scraper import scrape_news
from app import app
from models import NewsArticle, Base, engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os

# Ensure ENV is set to 'testing' in the test environment
os.environ['ENV'] = 'testing'

# Create a new session
Session = sessionmaker(bind=engine)
test_session = Session()

def test_scrape_news():
    # Clear DB before the test
    test_session.query(NewsArticle).delete()
    test_session.commit()

    scrape_news()  # Run the scraper

    # Query the database for the scraped articles
    articles = test_session.query(NewsArticle).all()
    print(f"Test DB Articles after scraping: {articles}")  # Debugging output

    # Assert that articles have been scraped and added to the DB
    assert len(articles) > 0  # Ensure at least one article is scraped
    print(f"Number of articles in DB after scrape: {len(articles)}") # Debugging

    assert articles[0].headline is not None

    # Close the session at the end of the test
    test_session.close()
