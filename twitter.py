import requests
import twitter_config

def search_tweets(query, max_results=10):
    headers = {
        "Authorization": f"Bearer {twitter_config.bearer_token}"
    }

    filtered_query = f"{query} -is:retweet"
    params = {
        "query": filtered_query,
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "author_id,created_at,conversation_id"
    }

    url = "https://api.twitter.com/2/tweets/search/recent"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(" Error fetching tweets:", response.status_code, response.text)
        return

    tweets = response.json().get("data", [])
    if not tweets:
        print("No tweets found.")
        return

    print(f"\n✅ Found {len(tweets)} tweets:\n")
    for i, tweet in enumerate(tweets, 1):
        print(f"\n📝 Tweet #{i}")
        print(f"Time: {tweet['created_at']}")
        print(f"Text: {tweet['text']}")
        print(f"Conversation ID: {tweet['conversation_id']}")

if __name__ == "__main__":
    search_query = input("Enter a topic to search on Twitter: ").strip()
    search_tweets(search_query, max_results=10)
