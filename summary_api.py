# social_summary_api.py — Unified FastAPI Swagger-based Summary Service

from fastapi import FastAPI
from pydantic import BaseModel
import praw
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv
from agno.agent import Agent
from datetime import datetime

# Load credentials
load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Configure APIs
genai.configure(api_key=GEMINI_API_KEY)
llm = genai.GenerativeModel("models/gemini-1.5-flash")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

app = FastAPI()

# Agent for summarization
class SocialAgent(Agent):
    def summarize(self, content: str) -> str:
        prompt = f"""
        Summarize the following Reddit and Twitter content in bullet points.
        Highlight trends, topics, and user sentiments.
        Format the summary like a clean report with clear section headings.

        {content}
        """
        response = llm.generate_content(prompt)
        return response.text.replace("**", "")

agent = SocialAgent()

# Request schema
class SummaryRequest(BaseModel):
    topic: str
    subreddit: str = "all"
    start_date: str = None
    end_date: str = None

# Helpers
def convert_to_timestamp(date_str):
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp()) if date_str else None

def fetch_reddit(topic, subreddit, start_ts, end_ts):
    subreddit_obj = reddit.subreddit(subreddit)
    results = subreddit_obj.search(topic, sort="relevance", limit=10)
    content = ""
    for post in results:
        post_ts = int(post.created_utc)
        if start_ts and end_ts and not (start_ts <= post_ts <= end_ts):
            continue
        content += f"Post: {post.title}\n"
        try:
            post.comments.replace_more(limit=0)
            for c in post.comments.list()[:5]:
                content += f"Comment: {c.body.strip()[:300]}\n"
        except:
            continue
    return content

def fetch_twitter(topic):
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    params = {
        "query": f"{topic} -is:retweet",
        "max_results": 10,
        "tweet.fields": "author_id,created_at,conversation_id"
    }
    url = "https://api.twitter.com/2/tweets/search/recent"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return ""
    tweets = response.json().get("data", [])
    return "\n".join([f"Tweet: {tweet['text']}\nTime: {tweet['created_at']}" for tweet in tweets])

@app.post("/summarize")
def summarize(request: SummaryRequest):
    start_ts = convert_to_timestamp(request.start_date)
    end_ts = convert_to_timestamp(request.end_date)

    reddit_data = fetch_reddit(request.topic, request.subreddit, start_ts, end_ts)
    twitter_data = fetch_twitter(request.topic)

    combined = reddit_data + "\n" + twitter_data

    if not combined.strip():
        return {"summary": "No content found for the given input."}

    summary = agent.summarize(combined)
    return {"summary": summary}
