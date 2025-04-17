# Routes

import io
import os
import shutil
from flask import Flask, Response, jsonify, redirect, render_template, request, url_for, flash 
from models import Weather, add_article_to_index, create_or_open_index, search_articles_complex_1, search_articles_complex_2, session, NewsArticle, CommunityArticle
from sentiment_and_summary import get_sentiment_and_summary
from summary import get_summary
from weather import get_weather
import logging
from models import search_articles
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg') 
from config import Config

app = Flask(__name__) 
app.secret_key = 'secret'


app.config["DATABASE_URL"] = Config.DATABASE_URL
app.config["NEWS_SITE_USERNAME"] = Config.NEWS_SITE_USERNAME
app.config["NEWS_SITE_PASSWORD"] = Config.NEWS_SITE_PASSWORD

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.before_request
def refresh_session():
    session.close()  # Rollback any pending transactions
    session.expire_all()  # Ensure fresh data is loaded

# Root for homepage
@app.route('/')
# Index function to execute when user navigates to root URL
def index():
    try:
        session.expire_all() # Ensures the session fetches fresh data
        page = request.args.get('page', 1, type=int) # Retrieves the page query parameter from the URL
        per_page = 5 # Number of articles per page

        #Fetch paginated news articles
        total_articles = session.query(NewsArticle).count() # Counts all articles
        total_pages = (total_articles + per_page - 1) // per_page # Calculate total pages and round up when needed

        # Queries NewsArticle table in the database to retrieve subset of records and stores in news_article variable as a list of NewsArticle objects 
        news_articles = session.query(NewsArticle).offset((page - 1) * per_page).limit(per_page).all() # Offset skips the articles that appear on previous page and limit fetches the 5 per page
        community_articles = session.query(CommunityArticle).order_by(CommunityArticle.created_at.desc()).all()
        
        # Fetch weather data
        weather_data = session.query(Weather).first()
        # Returns rendered HTML template and passes news_articles to template as articles
        return render_template(
            'index.html', articles=news_articles, weather=weather_data, community_articles=community_articles,
            page=page, total_articles=total_articles, per_page=per_page, total_pages=total_pages
        )
    except Exception as e:
        logging.error(f"Error loading homepage: {e}")
        flash("An error occurred while loading the page. Please try again", "error")
        return render_template('index.html', articles=[], weather=[], page=1, total_articles=0, per_page=5, total_pages=1)


# Route to update the current weather
@app.route('/update_weather', methods=['POST'])
# Function to update the weather
def update_weather():
    try:
        # Call  get_weather to run API GET request
        get_weather()
        flash("Weather updated successfully!", "success")
        # Returns rendered HTML template 
    except Exception as e:
        logging.error(f"Error updating weather: {e}")
        flash("Failed to update weather data. Please try again.", "error")
    return redirect(url_for('index'))

# Route for search bar to allow users to search articles by headline
@app.route('/search', methods = ['GET'])
def search():
    query = request.args.get('query', '') # Retrieves the value of the query parameter named 'query' from the request. Default is an empty string
    search_type = request.args.get('search_type', 'headline_summary')  # Retrieves the selected search type (default: 'headline_summary')
    try:
        if query: # If search term was entered
            
            # Call the appropriate search function based on the search type selected
            if search_type == 'headline_summary':
                results = search_articles_complex_1(query)  # Search across headline & summary
            elif search_type == 'wildcard_phrase':
                results = search_articles_complex_2(query)  # Search with wildcards or phrase
            else:
                results = []
                flash("Invalid search type selected.", "error")
            if not results:
                flash("No articles found for your search.", "info")
        else:
            results = [] # If no search term entered results is assigned empty list
            flash("Please enter a search term.", "warning")
        
        # Fetch weather data so it's always available
        weather_data = session.query(Weather).first()

        # Ensure pagination variables are always passed, even for searches
        total_articles = len(results)
        per_page = 5 # Keep it consistent with the main page
        total_pages = (total_articles + per_page - 1) // per_page
        page = 1 # Default to the first page when searching 

        # Renders index.html and passes results to the template for display
        return render_template('index.html', articles=results, weather=weather_data, 
                                page=page, total_articles=total_articles, 
                                per_page=per_page, total_pages=total_pages) 
    except Exception as e:
        logging.error(f"Error searching articles: {e}")
        flash("An error occurred during search. Please try again.", "error")
        return render_template('index.html', articles=[], page=1, total_articles=0, per_page=5, total_pages=1)
    
# Route to re-scrape for updated articlees
@app.route('/scrape', methods = ['POST'])
def scrape():
    try:
        session.expire_all() # Tells SQLAlchemy session to expire all instances it has loaded 
        session.commit() # Commits pending transactions to the database to ensure the session is clean

        from scraper import scrape_news # Imports scrape_news
        # scrape_news() # Calls scrape_news function to re-scrape for articles
        scraped_articles = scrape_news()

        for article in scraped_articles:
            add_article_to_index(article)  # Add each scraped article to the Whoosh index

        flash("Yay! News articles updated successfully!", "success")
        # session.expire_all()
        # session.commit() # Ensures the database updates before redirecting
    except Exception as e:
        logging.error(f"Error scraping articles: {e}")
        flash("Failed to update news articles. Please try again.", "error")
        return redirect(url_for('index')) # Redirect to the homepage

# Route to add new articles 
@app.route('/add', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST': # Checks if the request method is POST which means the form has been submitted
        try:
            # Retrieves the values from the submitted form data
            headline = request.form['headline']
            summary = request.form['summary']
            link = request.form['link']
        
            # Checks if headline or link are missing. If either is missing it returns an error message and 400 status code
            if not headline or not link:
                flash("Headline and link are required!", "error")
                return render_template('add_article.html')

            # Creates new NewsArticle object with the inputed headline, summary, and link.
            new_article = NewsArticle(headline=headline, summary=summary, link=link)
            session.add(new_article) # Adds the new article to the database session
            session.commit() # Commits the session to save the new article to the database
            
            # Add the new article to the Whoosh index
            add_article_to_index(new_article)
            
            flash("Article added successfully!", "success")
            return redirect(url_for('index')) # Redirect to the homepage
        
        except Exception as e:
            session.rollback() # Rollback in case of error
            logging.error(f"Error adding article: {e}")
            flash("Failed to add article. Please try again.", "error")
            return render_template('add_article.html')

    return render_template('add_article.html') # If the request method is GET, it renders the add_article.html template

@app.route('/add_community', methods=['GET', 'POST'])
def add_community_article():
    if request.method == 'POST':
        try:
            username = request.form['username']
            title = request.form['title']
            content = request.form['content']
            link = request.form['link']
            author = request.form['author']

            if not username or not title or not content or not link or not author:
                flash("All fields are required", "error")
                return render_template('add_community_article.html')
            
            new_article = CommunityArticle(username=username, title=title, content=content, link=link, author=author)
            session.add(new_article)
            session.commit()

            flash("Community article added successfully!", "success")
            return redirect(url_for('index'))
        
        except Exception as e:
            session.rollback()
            logging.error(f"Error adding community article: {e}")
            flash("Failed to add article. Please try again.", "error")
            return render_template('add_community_article.html')
        
    return render_template('add_community_article.html')

# Route to edit an article based on id
@app.route('/edit/<int:id>', methods = ['GET', 'POST'])
def edit_article(id):
    try:
        article = session.query(NewsArticle).get(id) # Gets the article from the database with the specified id

        if not article: # If the article does not exist, it returns error message and 404 status code
            flash("Article not found!", "error")
            return redirect(url_for('index')) # Redirect to the homepage

        if request.method == 'POST': # Checks if the request method is POST which means the form was submitted
            # Retrieves the values from the submitted form data
            article.headline = request.form['headline']
            article.summary = request.form['summary']
            article.link = request.form['link']
            session.commit() # Commits the session to save the updated article to the database
            flash("Article updated successfully!", "success")
            return redirect(url_for('index')) # Redirect to the homepage
    
        return render_template('edit_article.html', article=article) # If the request method is GET, it renders the edit_article.html template and passes article object to the template
    except Exception as e:
        logging.error(f"Error editing article {id}: {e}")
        flash("An error occurred while updating the article.", "error")
        return redirect(url_for('index')) # Redirect to the homepage

# Route to delete an article by id
@app.route('/delete/<int:id>', methods=['POST'])
def delete_article(id):
    try:
        # if request.form.get('_method') == 'DELETE': # checks if the form includes hidden _method field with the value 'DELETE' to emulate HTTP DELETE request
        article = session.query(NewsArticle).get(id) # Retrieves article from the database with the specified id 
            # Checks if the article exists, then deletes article from session
        if article:
            session.delete(article)
            session.commit() # Commits the session
            flash("Article deleted successfully!", "success")
        else:
            flash("Article not found!", "error") 
    except Exception as e:
        logging.error(f"Error deleting article {id}: {e}")
        flash("An error occurred while deleting the article. Please try again.", "error")
    return redirect(url_for('index')) # Redirects to the homepage

@app.route('/reindex', methods=['GET'])
def reindex():
    index_dir = "indexdir"

    # Delete the index directory to remove duplicates
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        print("Index deleted.")

    # Recreate the index
    ix = create_or_open_index()  
    writer = ix.writer()

    # Add fresh articles to the index
    articles = session.query(NewsArticle).all()
    for article in articles:
        writer.add_document(
            id=str(article.id),
            headline=article.headline,
            summary=article.summary or '',
            link=article.link
        )

    writer.commit()
    print("Reindexing completed.")
    return redirect(url_for('index'))

@app.route('/weather_chart')
def weather_chart():
    try:
        # Query weather data
        weather_entries = session.query(Weather).order_by(Weather.last_updated).all()

        if not weather_entries:
            return "No weather data available.", 404

        # Extract data
        dates = [entry.last_updated for entry in weather_entries]
        temps = [entry.temp for entry in weather_entries]

        # Create a plot
        plt.figure(figsize=(8, 4))
        plt.plot(dates, temps, marker='o', linestyle='-', color='b', label='Temperature')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.title('Weather Temperature Trends for Sonoma')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save plot to a buffer
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()  # Close the plot to free memory

        # Return the image as a response
        return Response(img.getvalue(), mimetype='image/png')

    except Exception as e:
        print(f"Error generating weather chart: {e}")
        return "Failed to generate weather chart.", 500
    
# @app.route('/api/sentiment-and-summary', methods=['POST'])
# def sentiment_and_summary():
#     data = request.get_json()
#     article_title = data.get('title')
#     article_content = data.get('content')

#     try:
#         result = get_sentiment_and_summary(article_title, article_content)

#         if result["summary"] and result["sentiment"]:
#             return jsonify({
#                 "summary": result["summary"],
#                 "sentiment": result["sentiment"]
#             })
#         else:
#             return jsonify({"error": "Incomplete AI response"}), 500
#     except Exception as e:
#         print(f"Error generating sentiment and summary: {e}")
#         return jsonify({"error": "Internal server error"}), 500

@app.route('/api/sentiment-and-summary', methods=['POST'])
def sentiment_and_summary():
    data = request.get_json()
    article_title = data.get('title')
    article_content = data.get('content')

    print(f"Received Article: {article_title}")

    try:
        # Get sentiment and summary from AI
        result = get_sentiment_and_summary(article_title, article_content)

        print(f"AI Summary: {result['summary']}")  # Debugging output
        print(f"Sentiment: {result['sentiment']}")  # Debugging output

        if result["summary"] and result["sentiment"]:
            # Find the article in the database by title
            article = session.query(NewsArticle).filter_by(headline=article_title).first()

            if article:
                print("Updating article in the database...")
                # Update the article with the sentiment and summary
                article.ai_summary = result["summary"]
                article.sentiment = result["sentiment"]

                # Commit the changes to the database
                session.commit()
                print("Database updated successfully!")

                return jsonify({
                    "ai_summary": result["summary"],
                    "sentiment": result["sentiment"]
                })
            else:
                print("Error: Article not found in database.")
                return jsonify({"error": "Article not found"}), 404
        else:
            return jsonify({"error": "Incomplete AI response"}), 500
    except Exception as e:
        print(f"Error generating sentiment and summary: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/api/summary', methods=['POST'])
def summary():
    data = request.get_json()
    article_title = data.get('title')
    article_content = data.get('content')

    try:
        result = get_summary(article_title, article_content)

        if result:
            return jsonify({"summary": result}), 200
        else:
            return jsonify({"error": "Incomplete AI response"}), 500
    except Exception as e:
        print(f"Error generating summary: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)