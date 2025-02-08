import requests
import json
import os
import textstat
import language_tool_python
import ai_utils
from ai_logger import logger

# Load API keys
ai_utils.load_api_keys()

GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
GHOST_ADMIN_API_URL = os.getenv("GHOST_ADMIN_API_URL")

# Files for storing and processing
PREDICTED_FILE = "predicted_titles.json"
IMG_URL_FILE = "img_urls.json"
DRAFTS_FILE = "blog_drafts.json"

QUALITY_THRESHOLD = 80  # Posts with a score below this go to manual review

# AI Quality Score Function
# Try initializing LanguageTool (Java)
try:
    tool = language_tool_python.LanguageTool("en-US")  # ✅ Java-based checker
    JAVA_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠️ Java-based grammar check failed: {e}")
    JAVA_AVAILABLE = False  # Fallback to GPT if Java isn't installed

def analyze_blog_quality(content):
    """
    Analyzes blog quality using readability and grammar checks.
    - Uses Java-based `language_tool_python` first.
    - Falls back to OpenAI GPT if Java isn't available.
    """
    try:
        readability_score = textstat.flesch_reading_ease(content)

        if JAVA_AVAILABLE:
            # ✅ Java-based grammar check
            matches = tool.check(content)
            grammar_errors = len(matches)
            corrected_content = tool.correct(content)
            logger.info("✅ Using Java-based grammar check.")
        else:
            # ❌ Java failed → Fallback to OpenAI
            corrected_content = ai_utils.openai_create(f"Fix any grammar mistakes in this text: {content}")
            grammar_errors = sum(1 for x, y in zip(content, corrected_content) if x != y)
            logger.info("🔄 Using OpenAI GPT as fallback.")

        # Calculate final quality score
        quality_score = max(0, 100 - grammar_errors)

        logger.info(f"📊 Readability Score: {readability_score}")
        logger.info(f"📝 Grammar Errors: {grammar_errors}")
        logger.info(f"🔢 Final Blog Quality Score: {quality_score}%")

        return quality_score

    except Exception as e:
        logger.error(f"❌ Quality analysis failed: {e}")
        return 50  # Default score if analysis fails



def save_draft_for_review(title, content, post_url):
    """
    Saves AI-generated blog drafts to a JSON file for manual review.
    """
    drafts = []

    # Load existing drafts
    if os.path.exists(DRAFTS_FILE):
        with open(DRAFTS_FILE, "r") as file:
            try:
                drafts = json.load(file)
            except json.JSONDecodeError:
                drafts = []

    # Add new draft
    drafts.append({
        "title": title,
        "content": content,
        "post_url": post_url,
        "status": "pending"
    })

    # Save back to file
    with open(DRAFTS_FILE, "w") as file:
        json.dump(drafts, file, indent=4)

    logger.info(f"✅ Draft saved for review: {title}")


def format_blog_post(title):
    """Generates a structured, SEO-optimized blog post using OpenAI."""
    prompt = f"""
        Write a well-structured, SEO-optimized blog post titled "{title}" in **valid HTML**.
        Use the following structure:

        <article>
        <h2>Introduction</h2>
        <p>Engaging introduction about the topic.</p>

        <h2>Key Sections</h2>
        <h3>Subheading 1</h3>
        <p>Details about the first key point.</p>

        <h3>Subheading 2</h3>
        <p>Details about the second key point.</p>

        <h2>Real-World Example</h2>
        <p>Provide a compelling real-world use case. Cite sources where applicable.</p>
        <blockquote>
            <p>Include a relevant statistic or expert quote.</p>
            <cite>Source Name - <a href='SOURCE_LINK' target='_blank'>SOURCE_LINK</a></cite>
        </blockquote>

        <h2>Conclusion</h2>
        <p>Summarize the blog and include a call-to-action.</p>
        </article>

        **Rules:**
        - **Use only valid HTML** (no Markdown).
        - **Cite sources** when including statistics, case studies, or expert opinions.
        - **Avoid wrapping the article in `<html>`, `<head>`, or `<body>`**.
    """


    try:
        response = ai_utils.openai_create(prompt, content="You are a professional SEO blogger.")
        
        if not response or len(response.strip()) < 50:  # Validate response length
            logger.error("❌ AI Model returned an empty or too-short response.")
            return None
        
        return response.strip()

    except Exception as e:
        logger.error(f"❌ AI Blog Generation Failed: {e}")
        return None



def post_to_ghost(title, content, image_url, manual_review=True):
    """Sends the AI-generated blog to Ghost CMS."""
    jwt_token = ai_utils.generate_token(GHOST_ADMIN_API_KEY)

    headers = {
        "Authorization": f"Ghost {jwt_token}",
        "Content-Type": "application/json"
    }

    cleaned_content = content.strip()

    # ✅ Ensure proper encoding
    mobiledoc_content = json.dumps({
        "version": "0.3.1",
        "atoms": [],
        "cards": [["html", {"html": f"<article>{cleaned_content}</article>"}]],
        "markups": [],
        "sections": [[10, 0]]
    })
    scheduled_time = ai_utils.get_scheduled_time()
    status = "draft" if manual_review else "scheduled"

    if status == "scheduled":
        data = {
            "posts": [
                {
                        "title": title,
                        "mobiledoc": mobiledoc_content,
                        "status": status,
                        "published_at": scheduled_time,
                        "excerpt": f"Learn about {title.lower()} in this detailed guide!",
                        "tags": ["AI", "Tech", "Guides"],
                        "feature_image": image_url
                }
            ]
        }
    else:
        data = {
            "posts": [
                {
                        "title": title,
                        "mobiledoc": mobiledoc_content,
                        "status": status,
                        "excerpt": f"Learn about {title.lower()} in this detailed guide!",
                        "tags": ["AI", "Tech", "Guides"],
                        "feature_image": image_url
                }
            ]
        }

    logger.info(f"📤 Blog POST Payload: {json.dumps(data, indent=4)}")

    # ✅ Log the full request payload before sending
    logger.info(f"📤 Sending Blog Post Request: {json.dumps(data, indent=4)}")

    try:
        response = requests.post(GHOST_ADMIN_API_URL, json=data, headers=headers)
        logger.info(f"🔄 Response Status: {response.status_code}")
        logger.info(f"🔄 Response Content: {response.text}")

        response.raise_for_status()  # Raise an error if the request fails

        blog_id = response.json()["posts"][0]["id"]
        preview_url = f"https://bytewhere.com/ghost/#/editor/post/{blog_id}"

        logger.info(f"✅ Blog '{title}' sent to Ghost!")

        if response.status_code == 201:
            ai_utils.notify_discord(f"✅ New AI blog ready for review: {title}!" if manual_review else f"✅ New AI blog scheduled: {title}!")
        else:
            ai_utils.notify_discord(f"❌ Blog posting failed: {response.text}")  # Notify failure too

        # Save draft for review if manual
        if manual_review:
            save_draft_for_review(title, content, preview_url)

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Blog posting failed: {e}")


# Blog Generation & Filtering Process
def generate_blog_and_post():
    """
    Uses AI-predicted title to generate a blog, analyze quality, and decide whether to publish or send to manual review.
    """
    try:
        with open(PREDICTED_FILE, "r") as file:
            best_title = json.load(file)[0]  # Pick the best one

        # Generates content for blog
        blog_content = format_blog_post(best_title)

        # Log the raw AI response before proceeding
        logger.info(f"📝 Generated Blog Content: {repr(blog_content)}")  # Log full response

        if not blog_content or len(blog_content.strip()) < 100:
            logger.error("❌ Failed to generate a valid blog post: Content is too short or empty.")
            logger.error(f"📝 Raw AI Response: {blog_content}")
            return


        # Load image URL safely
        img_url_data = ai_utils.load_json(IMG_URL_FILE, [])

        if not img_url_data or not isinstance(img_url_data, list) or len(img_url_data) == 0:
            logger.error("❌ Image URL data is empty or invalid.")
            img_url = "https://bytewhere.com/content/images/ai-blog.jpg"  # Fallback image
        else:
            img_url = img_url_data[0] if img_url_data[0].startswith("http") else f"https://bytewhere.com/content/images/{img_url_data[0]}"  # Ensure full URL

        logger.info("🔎 Checking for Blog Quality....")

        # Analyze quality
        quality_score = analyze_blog_quality(blog_content)

        if quality_score >= QUALITY_THRESHOLD:
            logger.info(f"✅ Auto-approving blog: {best_title} (Score: {quality_score}%)")
            post_to_ghost(best_title, blog_content, img_url, manual_review=False)
        else:
            logger.warning(f"⚠️ Low-quality blog detected (Score: {quality_score}%). Sending to manual review.")
            drafts = ai_utils.load_json(DRAFTS_FILE, [])
            drafts.append({"title": best_title, "content": blog_content, "score": quality_score})
            ai_utils.save_json(DRAFTS_FILE, drafts)
            # Sends blog post to dashboard for approve/rejection
            post_to_ghost(best_title, blog_content, img_url, manual_review=True)

    except Exception as e:
        logger.error(f"❌ Blog generation failed: {e}")

if __name__ == "__main__":
    generate_blog_and_post()
