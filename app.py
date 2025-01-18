from flask import Flask, render_template 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from scraper import NewsArticle

app = Flask(__name__)

engine = create_engine('sqlite:///news.db')
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    news_articles = session.query(NewsArticle).all()
    return render_template('index.html', articles=news_articles)

if __name__ == "__main__":
    app.run(debug=True)