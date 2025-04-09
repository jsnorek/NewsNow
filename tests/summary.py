import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_summary(title, content):
    text = f"{title}\n\n{content}"

    prompt = f"""
    Analyze the following news article and provide:
    1. A brief 1 sentence summary

    Article:
    {text}

    Format:
    Summary: ...
    """

    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content

    summary = ""
    
    for line in content.splitlines():
        if line.lower().startswith("summary:"):
            summary = line.split(":", 1)[1].strip()

    return summary