import openai
import requests
import json
import os
from ai_utils import load_api_keys, get_scheduled_time, generate_token
from ai_logger import logger

# Load API Keys
load_api_keys()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ghost API Credentials
GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
GHOST_ADMIN_API_URL = os.getenv("GHOST_ADMIN_API_URL")  # ✅ Correct API variable

# Discord Webhook
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# File storing AI-predicted blog titles
PREDICTED_FILE = "predicted_titles.json"


def openai_create(prompt, content="You are an AI assistant", model="gpt-4-turbo"):
    """
    Calls OpenAI's API to generate text using a specified model.

    :param prompt: The user input or task description.
    :param content: The system's instruction (default: "You are an AI assistant.")
    :param model: The GPT model to use (default: "gpt-4-turbo").
    :return: The AI-generated response or None if an error occurs.
    """
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": content},
                      {"role": "user", "content": prompt}]
        )
        
        if response and response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            logger.error("❌ OpenAI API returned an empty response.")
            return None

    except Exception as e:
        logger.error(f"❌ OpenAI API Error: {e}")
        return None


def notify_discord(message):
    """Sends notifications to Discord Webhook."""
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        logger.info("✅ Notification sent to Discord successfully!")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to send Discord notification: {e}")


def post_to_ghost(title, content, scheduled_time):
    """Schedules a blog post on Ghost."""
    jwt_token = generate_token(GHOST_ADMIN_API_KEY)
    headers = {
        "Authorization": f"Ghost {jwt_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Content-Type": "application/json"
    }

    logger.info(f"\n📢 Scheduling Post '{title}' for {scheduled_time} UTC...")

    mobiledoc_content = {
        "version": "0.3.1",
        "atoms": [],
        "cards": [["html", {"html": content}]],
        "markups": [],
        "sections": [[10, 0]]
    }

    data = {
        "posts": [
            {
                "title": title,
                "mobiledoc": json.dumps(mobiledoc_content),
                "status": "scheduled",
                "published_at": scheduled_time,
                "excerpt": "A guide to computer literacy and how to improve your tech skills.",
                "tags": ["tech", "AI", "blogging"],
                "feature_image": "https://bytewhere.com/content/images/computer-literacy.jpg"
            }
        ]
    }

    try:
        response = requests.post(GHOST_ADMIN_API_URL, json=data, headers=headers)
        response.raise_for_status()
        logger.info(f"✅ Blog: '{title}' scheduled successfully!")
        notify_discord(f"✅ A new blog: '{title}' has been scheduled for publishing!")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error posting blog: {e}")
        return None


def generate_blog_and_post():
    """Uses AI-predicted titles to generate and post blogs."""
    scheduled_time = get_scheduled_time()

    try:
        if not os.path.exists(PREDICTED_FILE) or os.path.getsize(PREDICTED_FILE) == 0:
            logger.error(f"❌ Predicted titles file '{PREDICTED_FILE}' is missing or empty.")
            return

        with open(PREDICTED_FILE, "r") as file:
            predicted_titles = json.load(file)

        if not predicted_titles or not isinstance(predicted_titles, list):
            logger.error(f"❌ Predicted titles file '{PREDICTED_FILE}' contains invalid data.")
            return

        best_title = predicted_titles[0]  # Pick the first title

        prompt = f"""
        Write an **SEO-optimized** blog post titled **'{best_title}'** with proper **HTML formatting**:
        
        - **Use <h2> for the main title**
        - **Use <h3> for subsections**
        - **Include bullet points (<ul><li>) and numbered lists (<ol><li>)**
        - **Wrap text paragraphs in <p>**
        - **Include a conclusion with a summary**
        - **Make sure it looks well-structured and clean**

        Output must be **pure HTML**, ready for Ghost API.
        ⚠️ **Important:** DO NOT wrap the content in ```html``` or triple backticks.
        """

        blog_content = openai_create(prompt, "You are an SEO blogger.")

        if blog_content:
            logger.info(f"✅ Blog generated: {best_title}")
            post_to_ghost(best_title, blog_content, scheduled_time)
        else:
            logger.error("❌ Failed to generate blog content.")

    except Exception as e:
        logger.error(f"❌ Blog generation failed: {e}")


if __name__ == "__main__":
    generate_blog_and_post()
