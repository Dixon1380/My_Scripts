import json
import random
import ai_utils
from ai_logger import logger
from ai_predictor import predict_best_title

TOPICS_FILE = "topics.json"
USED_TOPICS_FILE = "used_topics.json"
OUTPUT_FILE = "predicted_titles.json"
TITLE_LOG_FILE = "title_variations_log.json"


def get_unique_topic():
    """Selects a random topic while ensuring it hasn't been used recently."""
    topics = ai_utils.load_json(TOPICS_FILE, {"topics": []}).get("topics", [])
    used_topics = ai_utils.load_json(USED_TOPICS_FILE, [])

    available_topics = [topic for group in topics for topic in group if topic not in used_topics]

    if not available_topics:
        logger.info("🔄 Resetting used topics...")
        available_topics = [topic for group in topics for topic in group]
        used_topics = []

    selected_topic = random.choice(available_topics)
    
    # Ensure used_topics doesn't grow indefinitely
    if len(used_topics) > 50:
        used_topics.pop(0)

    used_topics.append(selected_topic)
    ai_utils.save_json(USED_TOPICS_FILE, used_topics)
    
    return selected_topic

def generate_title_variations(title):
    """Generates 5 AI-enhanced variations of the title and returns them."""
    prompt = f"""
    Generate 5 engaging, curiosity-driven variations of the blog title: "{title}". 
    - Use power words, emotional triggers, and curiosity hooks.
    - Keep each title under 70 characters for SEO.
    - Example improvements: 
      - Add numbers ("7 Ways to...")
      - Add urgency ("You NEED to Know This!")
      - Add intrigue ("The Truth About...")
    """

    try:
        ai_response = ai_utils.openai_create(prompt, content="You are an expert SEO title strategist.")
        generated_titles = ai_response.split("\n")

        # Clean up titles and remove any numbering or leading characters
        refined_titles = [title.lstrip("1234567890.- ").strip() for title in generated_titles if title.strip()]
        return refined_titles if refined_titles else [title]  # Fallback to original title if AI fails

    except Exception as e:
        logger.error(f"❌ AI Title Enhancement Failed: {e}")
        return [title]  # Fallback to original title

def rank_titles_with_ai(titles):
    """Ranks AI-generated title variations and picks the best one."""
    prompt = f"""
    Rank the following blog titles from best to worst based on engagement potential, SEO, and emotional appeal.
    Return only the best title.

    Titles:
    {json.dumps(titles, indent=2)}
    """

    try:
        ranked_title = ai_utils.openai_create(prompt, content="You are an expert SEO content strategist.")
        return ranked_title.strip() if ranked_title else titles[0]  # Fallback to first title

    except Exception as e:
        logger.error(f"❌ AI Ranking Failed: {e}")
        return titles[0]  # Fallback to first title

def generate_predicted_titles():
    """Predicts the best blog title, generates AI-enhanced variations, ranks them, and logs results."""
    best_title = predict_best_title()

    if not best_title:
        logger.warning("⚠️ No predicted title available. Falling back to topics.json.")
        best_title = get_unique_topic()

    # Generate AI variations
    title_variations = generate_title_variations(best_title)

    # Rank and select the best title
    best_ranked_title = rank_titles_with_ai(title_variations)

    # Log all generated titles for review
    log_data = {"original": best_title, "variations": title_variations, "selected": best_ranked_title}
    ai_utils.save_json(TITLE_LOG_FILE, log_data)

    # Save the selected title for the blog generator
    ai_utils.save_json(OUTPUT_FILE, [best_ranked_title])
    
    logger.info(f"✅ Selected best blog title: {best_ranked_title}")

if __name__ == "__main__":
    generate_predicted_titles()
