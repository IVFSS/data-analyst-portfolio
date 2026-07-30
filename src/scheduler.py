import schedule
import time
import logging
import signal
import sys
from pipeline import run_pipeline, init_database
from config import FETCH_INTERVAL_MINUTES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

running = True


def handle_signal(signum, frame):
    global running
    logger.info("Shutting down scheduler...")
    running = False


def job():
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Job failed: {e}")


def main():
    init_database()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info(f"Starting scheduler (interval: {FETCH_INTERVAL_MINUTES} min)")

    job()
    schedule.every(FETCH_INTERVAL_MINUTES).minutes.do(job)

    while running:
        schedule.run_pending()
        time.sleep(1)

    logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
