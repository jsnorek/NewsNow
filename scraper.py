# Stores data in SQLite database by setting up a SQLAlchemy model and saving the articles after scraping

import os
import time
import random
import logging
from bs4 import BeautifulSoup
from auth import login
from models import session, NewsArticle
from datetime import datetime, timezone
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# NPR News URL
SCRAPE_URL = "https://www.npr.org/sections/news/"

# Web scraping
def scrape_news():
    from models import session  # Ensure we're using the right session

    session.expire_all() # Forces SQLAlchemy to fetch fresh data from the database
    # Persistent session object
    session_requests = login() # This reduces the number of new connections created and can help avoid triggering anti-bot mechanisms that detect frequent logins from the same IP
    if not session_requests:
        logging.error("Login failed. Unable to scrape news")
        return

    # This header makes the scraper appear as a regular web browser rather than an automated bot
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = session_requests.get(SCRAPE_URL, headers=headers, timeout=10) # Send HTTP request to the specified url and save the response
        response.raise_for_status() # Raise error for bad HTTP responses

        soup = BeautifulSoup(response.text, 'html.parser') # Create a BeautifulSoup object by passing the two arguments of raw HTML and the parser we want to use
        # Find all article blocks on website
        articles = soup.find_all('article') # Searches for all h2 elements with the specified testid attribute (pulled from bbc website code)

        logging.info(f"Found {len(articles)} articles")  # Debugging statement for how many articles found

        # Print current articles in DB before scraping
        db_articles = session.query(NewsArticle).all()
        logging.info(f"Currently stored articles: {len(db_articles)}")
        for article in db_articles:
            logging.info(f"  DB Article: {article.headline} | {article.link}")

        # For loop that iterates over elements in articles list 
        for idx, article in enumerate(articles, start=1): # In each iteration of the loop, enumerate function provides a tuple: the first element (idx) is the current count of the loop (starting at 1), and the second element (article) is the current article element
            try:
                headline_tag = article.find('h2') # Finding the headline tag within the article
                summary_tag = article.find('p') # Finding the summary tag within the article
                link_tag = article.find('a') # Finding the first link tag within the article

                # Extract data with improved handling for missing elements
                headline = headline_tag.get_text(strip=True) if headline_tag else "No headline available" # Extracting the text from the headline tag
                summary = summary_tag.get_text(strip=True) if summary_tag else "No summary available" # Extracting the text from the summary tag
                link = link_tag['href'] if link_tag else "#"  # Getting the href attribute from the link tag

                # Ensure full link URL
                if link and not link.startswith('http'): # Ensures link is valid and complete
                    link = f'https://www.npr.org{link}' # Prepending the base URL if the link is relative

            # Improved debugging
            # print(f"Article {idx}:")
            # print(f"  Headline: {headline}")
            # print(f"  Summary: {summary}")
            # print(f"  Link: {link}")
            # print("-" * 50)

                logging.info(f"Article {idx}: {headline}")

                # Skip empty or placeholder articles
                if headline == "No headline available" or link == "#":
                    logging.warning(f"Skipping incomplete article {idx} due to missing headline or link")
                    continue

            # Debugging print to print scraped headline, summary, and link
            # print(f"Scraped article: {headline}\nSummary: {summary}\nLink: {link}\n")  # Debugging statement

                existing_article = session.query(NewsArticle).filter_by(link=link).first()

            # Save to the database if not already present
            # existing_article = session.query(NewsArticle).filter_by(headline=headline, link=link).first() # Querying the database to check if the article exists
            # existing_article = session.query(NewsArticle).filter(
            #     NewsArticle.headline == headline,
            #     NewsArticle.link == link
            # ).first()
            # if not existing_article:
            #     # Create new NewsArticle object for each article and add it to the session/database
            #     news_item = NewsArticle(headline=headline, summary=summary, link=link) # Creating a new NewsArticle object
            #     session.add(news_item)  # Adding the new article to the session
            # else:
            #     print(f"Skipped duplicate: {headline}") # Printing a message if the article is a duplicate
            

                if existing_article:
                    if existing_article.headline != headline or existing_article.summary != summary:
                        existing_article.headline = headline
                        existing_article.summary = summary
                        existing_article.updated_at = datetime.now(timezone.utc)  
                        # session.commit()
                        # session.close()
                        logging.info(f"✅ Updated existing article: {headline}")
                    else:
                        logging.info(f"⚠️ Skipped duplicate: {headline}")
                else:
                    news_item = NewsArticle(headline=headline, summary=summary, link=link)
                    session.add(news_item)
                    # session.commit()
                    # session.close()
                    logging.info(f"✅ Added new article: {headline}")
                # Random sleep to prevent rate limiting between requests. This mimics human behavior and helps prevent the server from detecting the scraper as a bot making rapid requests
                time.sleep(random.uniform(1, 3)) # Random sleep between 1 and 3 seconds
        
            except Exception as e:
                logging.error(f"Error scraping article {idx}: {e}")

            # Saves all the changes to the database
        session.commit() # Committing the session to save the articles to the database
        logging.info(f"Scraping complete. Total articles now stored: {len(session.query(NewsArticle).all())}")
        # To test before and after articles to make sure db is updated correctly
        # db_articles_after = session.query(NewsArticle).all()
            # print(f"Articles after scraping: {len(db_articles_after)}")
    except RequestException as e:
        logging.error(f"Network error while scraping: {e}")
    except Exception as e:
        logging.critical(f"Unexpected error during scraping: {e}")
    finally:
        session.close()

# Ensures function runs when script is executed directly
if __name__ == "__main__":
    scrape_news() # Calling the scrape_news function if the script is run directly