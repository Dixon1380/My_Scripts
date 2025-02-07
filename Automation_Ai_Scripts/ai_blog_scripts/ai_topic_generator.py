import json
import os
import random
from ai_logger import logger
from ai_predictor import predict_best_title  # ✅ Import prediction function

TOPICS_FILE = "topics.json"
USED_TOPICS_FILE = "used_topics.json"
OUTPUT_FILE = "predicted_titles.json"

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

def get_unique_topic():
    """Selects a random topic while ensuring it hasn't been used recently."""
    topics = load_json(TOPICS_FILE, {"topics": []}).get("topics", [])
    used_topics = load_json(USED_TOPICS_FILE, [])

    available_topics = [topic for group in topics for topic in group if topic not in used_topics]

    if not available_topics:
        logger.info("🔄 Resetting used topics...")
        available_topics = [topic for group in topics for topic in group]
        used_topics = []

    selected_topic = random.choice(available_topics)
    
    # Ensure used_topics doesn't grow indefinitely
    if len(used_topics) > 50:  # Example limit of 50
        used_topics.pop(0)  # Remove the oldest entry

    used_topics.append(selected_topic)
    save_json(USED_TOPICS_FILE, used_topics)
    
    return selected_topic

def generate_predicted_titles():
    """Uses AI model to predict the best-performing blog title and saves it."""
    best_title = predict_best_title()

    if not best_title:
        logger.warning("⚠️ No predicted title available. Falling back to topics.json.")
        best_title = get_unique_topic()

    save_json(OUTPUT_FILE, [best_title])
    logger.info(f"✅ Selected best blog title: {best_title}")

if __name__ == "__main__":
    generate_predicted_titles()
