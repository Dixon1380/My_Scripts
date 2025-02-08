import requests
import os
import json
import ai_utils
from ai_logger import logger

ai_utils.load_api_keys()

GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
GHOST_IMAGE_UPLOAD_URL = os.getenv("GHOST_IMAGE_UPLOAD_URL")

# Directory to store AI-generated images
IMAGE_CACHE_DIR = "ai_images"

# Files for storing and processing
PREDICTED_FILE = "predicted_titles.json"
IMG_URL_FILE = "img_urls.json"

def fetch_title():
    with open(PREDICTED_FILE, "r") as file:
        return json.load(file)[0]  # Pick the best one

def generate_and_upload():
    """Generates an image and uploads it to Ghost"""
    try:
        img_title = fetch_title()
        blog_img_url = ai_utils.generate_ai_image(img_title)

        # Generate JWT Token for Ghost
        jwt_token = ai_utils.generate_token(GHOST_ADMIN_API_KEY)

        blog_img_file = f"{img_title}.jpg"
        file_path = os.path.join(IMAGE_CACHE_DIR, blog_img_file)

        # Download the AI-generated image
        image_data = requests.get(blog_img_url, stream=True)
        if image_data.status_code == 200:
            with open(file_path, "wb") as img_file:
                for chunk in image_data.iter_content(1024):
                    img_file.write(chunk)
        else:
            logger.error("❌ Failed to download image")
            return

        logger.info(f"Uploading {blog_img_file} to {GHOST_IMAGE_UPLOAD_URL}")

        # Correcting how the file is uploaded
        with open(file_path, "rb") as img_file:
            files = {"file": (blog_img_file, img_file, "image/jpeg")}
            ghost_headers = {
                "Authorization": f"Ghost {jwt_token}"
            }

            upload_img_response = requests.post(GHOST_IMAGE_UPLOAD_URL, files=files, headers=ghost_headers)

        upload_img_response.raise_for_status()  # Ensure request succeeds

        uploaded_image_url = upload_img_response.json().get("images", [{}])[0].get("url", "")
        if not uploaded_image_url:
            raise ValueError("❌ Failed to retrieve uploaded image URL from Ghost response")

        logger.info(f"✅ Image uploaded to Ghost: {uploaded_image_url}")

        # Store image URL for ai_blog to fetch
        ai_utils.save_json(IMG_URL_FILE, [uploaded_image_url])  # Store as a list to avoid indexing errors
       
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to upload image to Ghost: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    generate_and_upload()
