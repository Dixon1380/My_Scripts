import jwt
import os
from datetime import datetime, timedelta, timezone
from ai_logger import logger
from dotenv import load_dotenv

def load_api_keys():
    """Loads API keys and verifies they are set."""
    load_dotenv()
    required_keys = ["OPENAI_API_KEY", "GHOST_ADMIN_API_KEY", "GHOST_CONTENT_API_KEY"]

    for key in required_keys:
        if not os.getenv(key):
            logger.warning(f"⚠️ Missing API Key: {key}")

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
    """
    Schedules a post at **9 AM UTC** at least 3 days ahead, avoiding weekends.
    - If the scheduled day is **Saturday**, move to **Monday**.
    - If the scheduled day is **Sunday**, move to **Monday**.
    """
    today = datetime.now()
    scheduled_date = today + timedelta(days=3)

    # Move post to Monday if it falls on a weekend
    while scheduled_date.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
        scheduled_date += timedelta(days=1)

    scheduled_time = scheduled_date.replace(hour=9, minute=0, second=0)

    # Convert to UTC (Ghost requires UTC timestamps)
    scheduled_time_utc = scheduled_time.astimezone(timezone.utc).isoformat()

    logger.info(f"📅 Scheduled Post for: {scheduled_time_utc} UTC")
    return scheduled_time_utc
