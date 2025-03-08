import logging
import os
import threading
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

import pytz

from app_backend import run_app
from get_occupancy_data import run_occupancy_data_collection

# Set Taipei timezone
TAIPEI_TZ = pytz.timezone("Asia/Taipei")

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Custom formatter to ensure Taipei timestamps in logs
class TaipeiFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        utc_dt = datetime.fromtimestamp(record.created, tz=timezone.utc)  # Get UTC timestamp
        taipei_dt = utc_dt.astimezone(TAIPEI_TZ)  # Convert to Taipei timezone
        return taipei_dt.strftime(datefmt if datefmt else "%Y-%m-%d %H:%M:%S")

# Define log filename (base name; actual filename will have date suffix)
log_filename = os.path.join(LOG_DIR, "occupancy_scraper.log")

# Configure TimedRotatingFileHandler to create a new log file at **midnight Taipei time**
file_handler = TimedRotatingFileHandler(
    log_filename, when="midnight", interval=1, backupCount=7, encoding="utf-8", utc=True
)
file_handler.suffix = "%Y-%m-%d"  # Appends date to rotated log files

# Apply custom formatter
formatter = TaipeiFormatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Get the root logger and explicitly add handlers
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)  # Add file handler
logger.addHandler(logging.StreamHandler())  # Also log to console

logging.getLogger("matplotlib").setLevel(logging.WARNING)
#TODO logging still buggy - does not create new log file at midnight


def main():
    # Start the occupancy data collection in a separate thread
    occupancy_data_thread = threading.Thread(target=run_occupancy_data_collection, daemon=True)
    occupancy_data_thread.start()
    run_app()
    occupancy_data_thread.join()
    

if __name__ == "__main__":
    main()