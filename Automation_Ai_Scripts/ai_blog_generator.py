import openai
import requests
import json
import jwt
from datetime import datetime, timedelta, timezone
import os
import random
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Ghost API Credentials
GHOST_ADMIN_API_KEY = os.getenv('GHOST_ADMIN_API_KEY')
GHOST_API_URL = os.getenv('GHOST_API_URL')  # Correct API version

# Discord Webhook for notifications
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')


# Custom Function to call openai.chat.completions
def openai_create(prompt, content="You are an AI assistant", model="gpt-4-turbo"):
    """
    Calls OpenAI's API to generate text using a specified model.

    :param prompt: The user input or task description.
    :param content: The system's instruction (default: "You are an AI assistant.")
    :param model: The GPT model to use (default: "gpt-4-turbo").
    :return: The AI-generated response.
    """
    try:
        output = openai.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": content},
                    {"role": "user", "content": prompt}]
        )
        return output
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return None

# Predefined Topics
TOPICS = [
    "The Importance of Digital Literacy in the Modern Age",
    "How to Stay Safe Online: Cybersecurity Tips for Beginners",
    "Mastering Computer Basics: A Guide for New Users",
    "How to Improve Your Digital Skills for Career Growth",
    "Understanding Cloud Computing and Why It Matters",
    "The Future of Work: How Digital Literacy Impacts Your Career",
    "A Beginner's Guide to Internet Safety and Privacy",
    "Top 10 Digital Tools Every Computer User Should Know",
    "The Role of Artificial Intelligence in Digital Literacy",
    "How to Protect Your Online Identity from Cyber Threats",
    "Digital Footprint Explained: How Your Online Presence Impacts Privacy and Security"
]

# File to store used topics
USED_TOPICS_FILE = "used_topics.json"

def load_used_topics():
    """Loads the list of previously used topics from a JSON file."""
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r") as file:
            try:
                result = json.load(file)
                print(f" from loadfunction: {result}")
                return result
            except Exception as e:
                print_message(f"Json Error: {e}")
    return []

def save_used_topic(topic):
    """Saves a used topic to the JSON file to prevent duplicates."""
    used_topics = load_used_topics()
    used_topics.append(topic)

    with open(USED_TOPICS_FILE, "w") as file:
        json.dump(used_topics, file)

def get_unique_topic():
    try:
        # Read the used topics file (ensure each topic is stored as a string)
        with open("used_topics.json", "r") as file:
            used_topics = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        used_topics = []

    # Ensure used_topics is a flat list (not a list of lists)
    used_topics = set(map(str, used_topics))

    # Ensure TOPICS is a flat list too
    available_topics = list(set(map(str, TOPICS)) - used_topics)

    if not available_topics:
        print("All topics have been used. Resetting topic list.")
        available_topics = list(map(str, TOPICS))
        used_topics = set()

    # Pick a random topic
    topic = random.choice(available_topics)

    # Append to used topics and save
    used_topics.add(topic)
    with open("used_topics.json", "w") as file:
        json.dump(list(used_topics), file, indent=4)

    return topic


# Notify Discord when blog is post. 
def notify_discord(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
       print_message("✅ Notification sent to Discord successfully!")
    else:
       print_message(f"❌ Failed to send Discord notification: {response.status_code} - {response.text}")

# Used for debugging and logging
def print_message(message):
    print(message)

# Generates the blog posts based on title given
def generate_blog(title):
    print_message(f" Blog: {title} is being generated.....")
    prompt = f"""
    Write an **SEO-optimized** blog post titled **'{title}'** with proper **HTML formatting**:

    - **Use <h2> for the main title**
    - **Use <h3> for subsections**
    - **Include bullet points (<ul><li>) and numbered lists (<ol><li>)**
    - **Wrap text paragraphs in <p>**
    - **Include a conclusion with a summary**
    - **Make sure it looks well-structured and clean**

    Output must be **pure HTML**, ready for Ghost API.
    """

    response = openai_create(prompt, "You are an SEO blog writer.")

    return response.choices[0].message.content.strip()

# Generates token for Ghost API 
def generate_token(key):
    key_id, secret = key.split(":")  # Extract key ID and secret

    iat = int(datetime.now().timestamp())
    exp = iat + 5 * 60  # Token expires in 5 minutes

    header = {"alg": "HS256", "kid": key_id, "typ": "JWT"}
    payload = {
        "exp": exp,
        "iat": iat,
        "aud": "/admin/"  # Correct audience format
    }

    # Generate the JWT token
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)
    return token

# Sends the post to Ghost
def post_to_ghost(title, content, scheduled_time):
    jwt_token = generate_token(GHOST_ADMIN_API_KEY)
    headers = {
        "Authorization": f"Ghost {jwt_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Content-Type": "application/json"
    }

    print_message(f"\n📢 Scheduling Post '{title}' for {scheduled_time} UTC...")

    print_message(f"Blog: {title} is being formated for Ghost....")
    # Use Mobiledoc to wrap HTML content correctly
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
                "published_at": scheduled_time, # Setting scheduled time
                "excerpt": "A guide to computer literacy and how to improve your tech skills.",  # Add SEO description
                "tags": ["computer literacy", "technology", "learning"],  # Add relevant tags
                "feature_image": "https://bytewhere.com/content/images/computer-literacy.jpg"  # Optional feature image
            }
        ]
    }
    response = requests.post(GHOST_API_URL, json=data, headers=headers)

    # Handle API Errors
    if response.status_code != 201:
        print_message("Post failed to send...\n")
        raise Exception(f"Ghost API Error: {response.status_code} - {response.text}")

    print_message(f"✅ {response.status_code} - Post successfully sent to Ghost for publishing.")
    notify_discord(f"✅ A new blog: {title} has been scheduled for publishing!")

    return response.json()

# Generates blog titles using a topic
def generate_blog_titles(topic, num_titles=5):
    print(f"🔹 Generating {num_titles} SEO-optimized blog titles for '{topic}'...")

    prompt = f"""
    Generate {num_titles} SEO-friendly blog titles about '{topic}'. 
    - Titles should be **engaging**, **click-worthy**, and **informative**.
    - Use power words like 'Ultimate Guide', 'Top 10', 'Everything You Need to Know'.
    - Titles must be under **70 characters** for SEO.
    - Avoid duplicate phrasing.
    """

    response = openai_create(prompt, "You are an SEO content strategist.")

    titles = response.choices[0].message.content.strip().split("\n")

    return [title.lstrip("1234567890. ").strip() for title in titles if title]

# Retrieves the current time to schedule new blog post for publishing
def get_scheduled_time():
    """
    Schedules a post 3 days ahead from the current day.
    If today is Saturday, schedule for Tuesday.
    If today is Sunday, schedule for Wednesday.
    Otherwise, schedule 3 days ahead.
    """

    today = datetime.now()
    scheduled_date = today + timedelta(days=3)

    # Ensure time is set to 9 AM
    scheduled_time = scheduled_date.replace(hour=9, minute=0, second=0)

    # Convert to UTC (Ghost requires UTC timestamps)
    scheduled_time_utc = scheduled_time.astimezone(timezone.utc).isoformat()

    print(f"📅 Scheduled Post for: {scheduled_time_utc} UTC")
    return scheduled_time_utc

# Generate topics based on niche
def generate_topics(niche="Computer and Digital Literacy"):
    prompt = f"Generate 5 blog topics related to {niche}. Make them engaging and SEO-friendly."

    response = openai_create(prompt, "You are an expert SEO blog writer.")

    topics = response.choices[0].message.content.split("\n")
    return [topic.strip("- ").strip() for topic in topics if topic.strip()]

# Variable to get a topic
topic = get_unique_topic()


# Main application
def main():
   blog_titles = generate_blog_titles(topic)
   scheduled_time = get_scheduled_time()
   for blog_title in blog_titles:
     blog_content = generate_blog(blog_title)
     post_to_ghost(blog_title,blog_content, scheduled_time)
   print_message("All blogs have been successfully posted to Ghost.")

if __name__ == "__main__":
    main()
