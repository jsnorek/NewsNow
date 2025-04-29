import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_summary(title, content):
    # Combine the title and content into a single string
    text = f"{title}\n\n{content}"

    # Construct the prompt
    prompt = f"""
    Analyze the following news article and provide:
    1. A brief 1 sentence summary

    Article:
    {text}

    Format:
    Summary: ...
    """

    # Make the API call
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return ""

    # Extract the AI's response
    content = response.choices[0].message.content

    # Parse the summary and sentiment
    summary = ""
    
    for line in content.splitlines():
        if line.lower().startswith("summary:"):
            summary = line.split(":", 1)[1].strip()

    return summary