# Database setup

from sqlalchemy import DateTime, Float, create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL, DEFAULT_CITY
import os
from datetime import datetime, timezone

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

# Define the Weather table
class Weather(Base): # New class that inherits from Base to map to database table
    __tablename__ = 'weather' # Specifies name of database table
    id = Column(Integer, primary_key=True) # Defines column named id which is an integer and primary key
    temp = Column(Float, nullable=False) # Defines column named temp
    city = Column(String, nullable=False, default=DEFAULT_CITY) # Defines column named city and the default is DEFAULT_CITY
    description = Column(String, nullable=False) # Defines column named description
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # Defines column named last_updated using a callable lambda function to dynamically assign a default value determined at runtime

# Create table if it doesn't exist
Base.metadata.create_all(engine)