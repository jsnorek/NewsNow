# Stores data in SQLite database by setting up a SQLAlchemy model and saving the articles after scraping

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.orm import sessionmaker, declarative_base

# Database setup with SQLite
engine = create_engine('sqlite:///news.db') # Creates a connection to the SQLite database named news.db
Session = sessionmaker(bind=engine) # Defines a factory to create new Session objects
session = Session() # Initializes a session to interact with the database
Base = declarative_base() # Creates a base class for model definitions

# Create structured representation of the data being scraped to store and retrieve data
class NewsArticle(Base): # New class that inherits from Base to map to database table
    __tablename__ = 'news_articles' # Specifies name of database table
    id = Column(Integer, primary_key=True) # Defines column named id which is an integer and primary key
    headline = Column(String) # Defines column to store strings for article headlines
    link = Column(String) # Defines column to store strings for urls of the articles

Base.metadata.create_all(engine) # Creates the news_articles table in database using the schema defined by the NewsArticle class which is inheritted from Base

# Web scraping
def scrape_news():  
    url = "https://www.bbc.com/news" # Target URL for scraping
    response = requests.get(url) # Send HTTP request to the specified url and save the response
    
    # Check to see if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser') # Create a BeautifulSoup object by passing the two arguments of raw HTML and the parser we want to use
        articles = soup.find_all('h2', attrs={'data-testid': 'card-headline'}) # Searches for all h2 elements with the specified testid attribute (pulled from bbc website code)
        print(f"Found {len(articles)} articles") # Prints the number of articles found

        # Loop through articles
        for article in articles:
            headline = article.text # Get text from headline
            link = article.find_parent('a')['href'] # Locates the parent tag that contains the URL
            if not link.startswith('http'): # Ensures link is valid and complete
                link= f'https://www.bbc.com{link}'

            # Debugging print to print scraped headline and link
            print(f"Scraped headline: {headline}")
            print(f"Link: {link}")

            # Create new NewsArticle object for each article and add it to the session/database
            news_item = NewsArticle(headline=headline, link=link)
            session.add(news_item)
    
        # Saves all the changes to the database
        session.commit()
    # Print error messages if request fails
    else:
        print("Failed to retrieve the webpage")
        print("Status code: {respone.status_code}")

# Ensures function runs when script is executed directly
if __name__ == "__main__":
    scrape_news()