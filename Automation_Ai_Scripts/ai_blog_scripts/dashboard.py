from flask import Flask, render_template, request, jsonify
import ai_utils
from ai_logger import logger
from ai_blog_generator import post_to_ghost

app = Flask(__name__)

DRAFTS_FILE = "drafts.json"

def load_drafts():
    """Loads draft blog posts pending approval."""
    return ai_utils.load_json(DRAFTS_FILE, [])

def save_drafts(drafts):
    """Saves the updated drafts list."""
    ai_utils.save_json(DRAFTS_FILE, drafts)

@app.route("/")
def dashboard():
    drafts = load_drafts()
    return render_template("dashboard.html", drafts=drafts)

@app.route("/approve", methods=["POST"])
def approve_post():
    """Approves a blog post and sends it to Ghost."""
    try:
        index = int(request.json.get("index"))
        drafts = load_drafts()

        if index < 0 or index >= len(drafts):
            return jsonify({"error": "Invalid post index"}), 400

        post = drafts.pop(index)
        save_drafts(drafts)

        post_to_ghost(post["title"], post["content"])
        logger.info(f"✅ Blog Approved: {post['title']}")
        ai_utils.notify_discord(f"✅ New AI blog was approved to be published: {post['title']}!")
        return jsonify({"message": "Post approved and published!"})

    except Exception as e:
        logger.error(f"❌ Approval failed: {e}")
        return jsonify({"error": "Approval failed"}), 500

@app.route("/reject", methods=["POST"])
def reject_post():
    """Rejects a blog post and removes it from drafts."""
    try:
        index = int(request.json.get("index"))
        drafts = load_drafts()

        if index < 0 or index >= len(drafts):
            return jsonify({"error": "Invalid post index"}), 400

        rejected_post = drafts.pop(index)
        save_drafts(drafts)
        logger.warning(f"❌ Blog Rejected: {rejected_post['title']}")

        return jsonify({"message": "Post rejected and removed."})

    except Exception as e:
        logger.error(f"❌ Rejection failed: {e}")
        return jsonify({"error": "Rejection failed"}), 500

