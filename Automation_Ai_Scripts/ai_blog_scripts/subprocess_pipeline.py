import subprocess
import time
from ai_logger import logger
from ai_utils import load_api_keys

# Load API keys at the beginning of execution
load_api_keys()


# Define tasks in the correct execution order
TASKS = [
    ("📥 Fetching engagement data from Ghost...", "ai_fetch_data.py"),
    ("📊 Running AI A/B Analysis...", "ai_ab_analysis.py"),
    ("🤖 Training AI Predictor...", "ai_predictor.py"),
    ("🔮 Generating AI-Predicted Blog Titles...", "ai_topic_generator.py"),
    ("🖼️ Generating and Uploading Blog Image...", "ai_image_generator.py"),
    ("📝 Generating and Publishing New Blog...", "ai_blog_generator.py")
]

def run_task(description, script_name):
    """Executes a subprocess, logs the result, and tracks execution time."""
    logger.info(description)
    start_time = time.time()  # Track start time

    try:
        result = subprocess.run(["python3", script_name], check=True, capture_output=True, text=True)
        elapsed_time = time.time() - start_time  # Compute time taken
        logger.info(f"✅ {script_name} completed successfully in {elapsed_time:.2f}s")

        # Capture output for debugging
        if result.stdout:
            logger.info(f"📄 Output from {script_name}:\n{result.stdout}")

        if result.stderr:
            logger.warning(f"⚠️ Warnings from {script_name}:\n{result.stderr}")

    except subprocess.CalledProcessError as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ {script_name} failed after {elapsed_time:.2f}s: {e}")

def run_pipeline():
    """Runs the full AI pipeline in sequence."""
    logger.info("🚀 Starting AI Blog Pipeline...")
    start_pipeline_time = time.time()

    for description, script in TASKS:
        run_task(description, script)

    total_pipeline_time = time.time() - start_pipeline_time
    logger.info(f"🎯 Full pipeline execution finished in {total_pipeline_time:.2f}s!")

if __name__ == "__main__":
    run_pipeline()
