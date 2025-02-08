import openai
from openai import OpenAI
import jwt
import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from ai_logger import logger
from dotenv import load_dotenv

def load_api_keys():
    """Loads API keys and verifies they are set."""
    load_dotenv()
    required_keys = [
        "OPENAI_API_KEY", 
        "GHOST_ADMIN_API_KEY", 
        "GHOST_CONTENT_API_KEY",
        "GHOST_ADMIN_API_URL",
        "GHOST_CONTENT_API_URL",
        "GHOST_IMAGE_UPLOAD_URL",
        "DISCORD_WEBHOOK_URL",
        "SMTP_SERVER",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "NOTIFY_EMAIL"
    ]

    for key in required_keys:
        if not os.getenv(key):
            logger.warning(f"⚠️ Missing API Key: {key}")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Default to 587 for TLS
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def notify_discord(message):
    """Sends blog updates to Discord."""
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        logger.info("✅ Notification sent to Discord!")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Discord notification failed: {e}")

def send_email_notification(title, preview_url):
    """Sends an email notification when a new AI-generated blog is ready for review."""
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, NOTIFY_EMAIL]):
        logger.error("❌ Email notification failed: Missing SMTP credentials in .env")
        return

    subject = f"📝 AI Blog Ready for Review: {title}"
    body = f"""
    <h2>AI-Generated Blog Ready for Review</h2>
    <p>The AI has created a new blog post titled <b>{title}</b>.</p>
    <p>Click the link below to review and edit the blog before publishing:</p>
    <p><a href="{preview_url}" target="_blank">{preview_url}</a></p>
    <br>
    <p>🚀 This is an automated message from your AI Pipeline.</p>
    """

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = NOTIFY_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, NOTIFY_EMAIL, msg.as_string())
        server.quit()

        logger.info(f"✅ Email notification sent for blog: {title}")

    except Exception as e:
        logger.error(f"❌ Failed to send email notification: {e}")


def openai_create(prompt, content="You are a professional writer."):
    """Generates content using OpenAI API."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": content}, {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"❌ OpenAI request failed: {e}")
        return None



def generate_ai_image(title):
    """
    Uses OpenAI to generate an image.
    """
    try:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
        GHOST_IMAGE_UPLOAD_URL = os.getenv("GHOST_IMAGE_UPLOAD_URL")

        if not OPENAI_API_KEY or not GHOST_ADMIN_API_KEY or not GHOST_IMAGE_UPLOAD_URL:
            raise ValueError("❌ Missing required environment variables")

        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Generate AI Image
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Generate an AI illustration for '{title}'",
            size="1024x1024",
            quality="standard",
            n=1
        )
        img_url = response.data[0].url  # Get the image URL from OpenAI
        logger.info(f"✅ AI Image Generated for Blog Post: {title}")
        return img_url
    except openai.OpenAIError as e:
        logger.error(f"❌ AI image generation failed: {e}")



def generate_token(key):
    """Generates a JWT token for Ghost API authentication."""
    try:
        if not key or ":" not in key:
            raise ValueError("Invalid API key format. Expected 'key_id:secret'.")

        key_id, secret = key.split(":")

        iat = int(datetime.now().timestamp())
        exp = iat + 5 * 60  # Token expires in 5 minutes

        header = {"alg": "HS256", "kid": key_id, "typ": "JWT"}
        payload = {"exp": exp, "iat": iat, "aud": "/admin/"}

        # Generate the JWT token
        token = jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)
        return token

    except Exception as e:
        logger.error(f"❌ Token generation failed: {e}")
        return None


def get_scheduled_time():
    """Schedules a post at 9 AM UTC at least 3 days ahead, avoiding weekends."""
    today = datetime.now()
    scheduled_date = today + timedelta(days=3)

    while scheduled_date.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
        scheduled_date += timedelta(days=1)

    scheduled_time_utc = scheduled_date.replace(hour=9, minute=0, second=0).astimezone(timezone.utc).isoformat()
    logger.info(f"📅 Scheduled Post for: {scheduled_time_utc} UTC")
    return scheduled_time_utc

def create_file(filename):
    if not os.path.exists(filename):
        open(filename, 'w').close()
    return filename

def load_json(file_path, default_value=None):
    """Loads JSON data from a file, returning a default value if the file is missing or corrupted."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON Error in {file_path}: {e}")
    return default_value or []

def save_json(file_path, data):
    """Saves data as JSON to a file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)