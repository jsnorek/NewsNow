# Database setup

# from ast import Or
from sqlalchemy import DateTime, Float, Text, create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
# from config import DATABASE_URL, DEFAULT_CITY
from config import Config
import os
from datetime import datetime, timezone

# Whoosh imports for search functionality
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

print(f"Database path: {os.path.abspath('news.db')}")

# Set up the database connection
engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define the NewsArticle table
class NewsArticle(Base): # New class that inherits from Base to map to database table
    __tablename__ = 'news_articles' # Specifies name of database table
    id = Column(Integer, primary_key=True)  # Defines column named id which is an integer and primary key
    headline = Column(String, nullable=False) # Defines column to store strings for article headlines
    summary = Column(String, nullable=True) # Defines column to store strings for summary of the articles
    link = Column(String, nullable=False) # Defines column to store strings for urls of the articles
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # Track updates

# Define the Weather table
class Weather(Base): # New class that inherits from Base to map to database table
    __tablename__ = 'weather' # Specifies name of database table
    id = Column(Integer, primary_key=True) # Defines column named id which is an integer and primary key
    temp = Column(Float, nullable=False) # Defines column named temp
    city = Column(String, nullable=False, default=Config.DEFAULT_CITY) # Defines column named city and the default is DEFAULT_CITY
    description = Column(String, nullable=False) # Defines column named description
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # Defines column named last_updated using a callable lambda function to dynamically assign a default value determined at runtime

class CommunityArticle(Base):
    __tablename__ = 'community_articles'
    id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    link = Column(Text, nullable=False)
    author = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Create table if it doesn't exist
Base.metadata.create_all(engine)

# Whoosh schema and index setup
news_article_schema = Schema(
    id=ID(stored=True, unique=True),
    headline=TEXT(stored=True),
    summary=TEXT(stored=True),
    link=TEXT(stored=True)
)

# Set up the Whoosh index
index_dir = 'whoosh_index'
if not os.path.exists(index_dir):
    os.mkdir(index_dir)

def create_or_open_index():
    index_dir = "indexdir"

    # Define schema
    schema = Schema(
        id=ID(stored=True, unique=True),
        headline=TEXT(stored=True),
        summary=TEXT(stored=True),
        link=TEXT(stored=True)
    )

    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        return create_in(index_dir, schema)  # Creates a new index

    return open_dir(index_dir)

# Function to add a news article to the Whoosh index
def add_article_to_index(article):
    ix = create_or_open_index()
    writer = ix.writer()
    writer.add_document(
        id=str(article.id),
        headline=article.headline,
        summary=article.summary or '',
        link=article.link
    )
    writer.commit()

# Function to search articles in the Whoosh index
def search_articles(query):
    ix = create_or_open_index()
    searcher = ix.searcher()
    query_parser = QueryParser("headline", ix.schema)
    parsed_query = query_parser.parse(query)

    # Log the query and parsed query to see what is being searched
    print(f"Searching for: {query}")
    print(f"Parsed query: {parsed_query}")
    
    results = searcher.search(parsed_query)
    print(f"Search results: {len(results)} articles found")

    return results

# Complex Query 1: Search in both headline and summary
def search_articles_complex_1(query):
    ix = create_or_open_index()
    searcher = ix.searcher()

    # Use MultifieldParser for combining queries
    parser = MultifieldParser(["headline", "summary"], ix.schema, group=OrGroup)
    combined_query = parser.parse(query)

    results = searcher.search(combined_query)
    return results

# Complex Query 2: Search with wildcards or exact phrases
def search_articles_complex_2(query):
    ix = create_or_open_index()
    searcher = ix.searcher()
    
    # Using phrase or wildcard search
    query_parser = QueryParser("headline", ix.schema)
    parsed_query = query_parser.parse(f'"{query}" OR {query}*')  # Exact phrase or starts with query
    
    results = searcher.search(parsed_query)
    return results