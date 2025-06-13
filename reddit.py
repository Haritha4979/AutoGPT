import praw
from datetime import datetime
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# 🟦 Get user input
print("🔎 Reddit Post & Comment Extractor\n")
query = input("Enter a topic to search on Reddit: ").strip()
subreddit_name = input("Enter subreddit name (default: all): ").strip() or "all"
start_date = input("Enter start date (YYYY-MM-DD): ").strip()
end_date = input("Enter end date (YYYY-MM-DD): ").strip()

# Convert date input to timestamps
start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

#  Search Reddit posts
subreddit = reddit.subreddit(subreddit_name)
results = subreddit.search(query, sort="relevance", limit=10)

#  Filter posts by date range
filtered_posts = []
for post in results:
    post_ts = int(post.created_utc)
    if start_ts <= post_ts <= end_ts:
        filtered_posts.append(post)

#  If no posts found in date range
if not filtered_posts:
    print("\n No posts found in the given date range.")
else:
    print(f"\n Top Reddit posts about: {query} (from {start_date} to {end_date})\n")

    for post in filtered_posts:
        print(f"Title: {post.title}")
        print(f"Subreddit: {post.subreddit}")
        print(f"Score: {post.score}")
        print(f"URL: {post.url}\n")

        try:
            post.comments.replace_more(limit=0)
            top_comments = post.comments.list()[:5]
            print("Top Comments:")
            for i, comment in enumerate(top_comments, 1):
                print(f"{i}. {comment.body.strip()[:300]}")  # Limit long comments
            print("\n" + "-" * 80 + "\n")
        except Exception as e:
            print(f" Error fetching comments: {e}\n")




