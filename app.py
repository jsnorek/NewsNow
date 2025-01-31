from flask import Flask, render_template, request 
from models import session, NewsArticle

app = Flask(__name__) 

# Root for homepage
@app.route('/')
# Index function to execute when user navigates to root URL
def index():
    # Queries NewsArticle table in the database to retrieve all records and stores in news_article variable as a list of NewsArticle objects 
    news_articles = session.query(NewsArticle).all()
    # Returns rendered HTML template and passes news_articles to template as articles
    return render_template('index.html', articles=news_articles)

# Route for search bar 
@app.route('/search', methods = ['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        results = session.query(NewsArticle).filter(NewsArticle.headline.contains(query)).all()
    else:
        results = []
    return render_template('index.html', articles=results)

if __name__ == "__main__":
    app.run(debug=True)