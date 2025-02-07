import schedule
import time
import subprocess
import signal
import sys
from ai_logger import logger

def run_scheduled_pipeline():
    """Triggers the AI pipeline at a scheduled time."""
    logger.info("⏳ Running scheduled AI pipeline...")
    
    try:
        result = subprocess.run(["python3", "subprocess_pipeline.py"], check=True, capture_output=True, text=True)
        
        logger.info(f"✅ AI pipeline completed successfully!\nOutput:\n{result.stdout}")

        if result.stderr:
            logger.warning(f"⚠️ Warnings from pipeline:\n{result.stderr}")

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ AI pipeline execution failed: {e}")

# Schedule the pipeline to run every Monday at 2 AM
schedule.every().monday.at("02:00").do(run_scheduled_pipeline)
logger.info("🕒 Scheduled AI pipeline to run every Monday at 2 AM.")

# Graceful shutdown handling
def signal_handler(sig, frame):
    logger.info("🛑 Shutting down AI scheduler gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("🚀 AI Scheduler started. Waiting for scheduled tasks...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
