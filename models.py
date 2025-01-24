from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL
import os

print(f"Database path: {os.path.abspath('news.db')}")

# Set up the database connection
engine = create_engine(DATABASE_URL)
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

# Create table if it doesn't exist
Base.metadata.create_all(engine)