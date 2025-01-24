from flask import Flask, render_template 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from scraper import NewsArticle

app = Flask(__name__) 

# Set up connection to SQLite database "news.db"
# Needs connection to query the database to display news articles on the site
engine = create_engine('sqlite:///news.db')
Session = sessionmaker(bind=engine)
session = Session()

# Root for homepage
@app.route('/')
# Index function to execute when user navigates to root URL
def index():
    # Queries NewsArticle table in the database to retrieve all records and stores in news_article variable as a list of NewsArticle objects 
    news_articles = session.query(NewsArticle).all()
    # Returns rendered HTML template and passes news_articles to template as articles
    return render_template('index.html', articles=news_articles)

if __name__ == "__main__":
    app.run(debug=True)