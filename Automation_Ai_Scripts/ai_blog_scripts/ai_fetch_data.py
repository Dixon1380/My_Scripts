import requests
import json
import os
from datetime import datetime
import ai_utils
from ai_logger import logger


LOG_JSON_FILE = "fetch_data.json"

# Load API keys
ai_utils.load_api_keys()
GHOST_CONTENT_API_KEY = os.getenv("GHOST_CONTENT_API_KEY")
GHOST_CONTENT_API_URL = os.getenv("GHOST_CONTENT_API_URL")


def fetch_published_posts():
    """
    Fetches **published** blog posts from Ghost API and logs engagement data.
    """
    if not GHOST_CONTENT_API_KEY or not GHOST_CONTENT_API_URL:
        logger.error("❌ Ghost API credentials are missing!")
        return

    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(f"{GHOST_CONTENT_API_URL}/posts/?key={GHOST_CONTENT_API_KEY}&filter=visibility:public&limit=5", headers=headers)
        response.raise_for_status()  # Raise HTTP error if request fails
        blog_posts = response.json().get("posts", [])

        log_data = []
        for post in blog_posts:
            title = post.get("title", "Untitled Post")
            meta = post.get("meta", {})  # Safely access meta
            views = meta.get("views", 0)
            clicks = meta.get("clicks", 0)
            shares = meta.get("shares", 0)

            log_data.append({
                "title": title,
                "timestamp": datetime.now().isoformat(),
                "clicks": clicks,
                "shares": shares,
                "views": views
            })

        with open(LOG_JSON_FILE, "w") as file:
            json.dump(log_data, file, indent=4)

        logger.info("✅ Engagement data updated.")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error fetching blog data: {e}")

if __name__ == "__main__":
    ai_utils.create_file(LOG_JSON_FILE)
    fetch_published_posts()
