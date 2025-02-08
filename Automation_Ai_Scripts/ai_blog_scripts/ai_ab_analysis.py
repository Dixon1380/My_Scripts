import json
import os
import pandas as pd
from ai_logger import logger
import ai_utils

# Files for processing and storing data
LOG_JSON_FILE = "fetch_data.json"  # Raw JSON data
OUTPUT_CSV = "ab_results.csv"  # Structured CSV output


def load_engagement_data():
    """Loads and validates engagement data from JSON file."""
    if not os.path.exists(LOG_JSON_FILE):
        logger.error(f"❌ Engagement data file '{LOG_JSON_FILE}' not found.")
        return []

    if os.path.getsize(LOG_JSON_FILE) == 0:
        logger.warning(f"⚠️ Engagement data file '{LOG_JSON_FILE}' is empty.")
        return []

    try:
        with open(LOG_JSON_FILE, "r") as file:
            data = json.load(file)

            if not isinstance(data, list):
                logger.error(f"❌ Invalid format in '{LOG_JSON_FILE}'. Expected a list.")
                return []

            if not data:
                logger.warning(f"⚠️ No engagement data found in '{LOG_JSON_FILE}'.")
                return []

            logger.info(f"✅ Loaded {len(data)} engagement records.")
            return data

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decoding error in '{LOG_JSON_FILE}': {e}")
        return []


def process_engagement_data():
    """Processes engagement logs and converts them into structured CSV data."""
    data = load_engagement_data()
    
    if not data:
        logger.warning("⚠️ No data to process. Skipping CSV export.")
        return

    try:
        df = pd.DataFrame(data)

        # Ensure required columns exist
        required_columns = ["title", "timestamp", "clicks", "shares", "views"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0  # Fill missing columns with default values

        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"✅ Engagement data saved to CSV: {OUTPUT_CSV}")

    except Exception as e:
        logger.error(f"❌ Error processing engagement data: {e}")


if __name__ == "__main__":
    ai_utils.create_file(OUTPUT_CSV)
    process_engagement_data()
