import datetime
import json
import logging
import os
from time import sleep
from typing import List, Tuple

import pytz  # pip install pytz
import requests
import schedule  # pip install schedule
from bs4 import BeautifulSoup

# Set timezone to Taipei
TAIPEI_TZ = pytz.timezone("Asia/Taipei")

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Generate log file name based on current date
log_filename = os.path.join(LOG_DIR, f"occupancy_scraper_{datetime.datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename),  # Log to daily file
        logging.StreamHandler()  # Also log to console
    ]
)


def fetch_occupancy() -> Tuple[List[int], str]:
    # URL of the page
    url: str = "https://rent.pe.ntu.edu.tw/"

    # Simulate a browser request (add headers to prevent blocking)
    headers: str = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    # Fetch the page content
    response = requests.get(url, headers=headers)

    # Parse the page
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the relevant data
    people_counts: List[str] = [span.text.strip() for span in soup.select(".ICI span")]

    people_counts: List[int] = [
        int(count) for count in people_counts if count.isdigit()
    ]

    update_time: str = (
        soup.select_one(".CMCUpTime").text.strip().split(" ")[1:]
        if soup.select_one(".CMCUpTime")
        else "N/A"
    )

    return people_counts, update_time


def save_occupancy_data(
    update_time: str, fitness_room_people_count: int, swimming_pool_people_count: int
) -> None:
    # Prepare the data entry
    data_entry = {
        "fitness_room_people_count": fitness_room_people_count,
        "pool_people_count": swimming_pool_people_count,
    }

    # Load existing data if available
    try:
        with open("occupancy_data/occupancy_data.json", "r") as file:
            all_data = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        all_data = {}

    update_day: str = update_time[0]
    update_time: str = update_time[1]

    # Ensure the date key exists
    if update_day not in all_data:
        all_data[update_day] = {}

    if update_time in all_data[update_day]:
        logging.warning(
            f"Data already exists for {update_day} {update_time} - skipping"
        )
        return

    # Store data with timestamp
    all_data[update_day][update_time] = data_entry

    # Write the updated data back to the JSON file
    with open("occupancy_data/occupancy_data.json", "w") as file:
        json.dump(all_data, file, indent=4)


def update_occupancy_data():
    now = datetime.datetime.now(TAIPEI_TZ)
    if not (8 <= now.hour < 22):
        logging.debug("Outside of gym hours (08:00-22:00 Taipei time). Skipping...")
        return

    people_counts, update_time = fetch_occupancy()

    if len(people_counts) == 0:
        logging.error("Failed to fetch occupancy data")
        return

    if update_time == "N/A":
        logging.error("Failed to fetch update time")
        return

    fitness_room_people_count: int = people_counts[0]
    swimming_pool_people_count: int = people_counts[3]

    logging.debug(
        f"Succesfully fetched data: {fitness_room_people_count} people in the fitness room, {swimming_pool_people_count} people in the swimming pool"
    )

    save_occupancy_data(
        update_time, fitness_room_people_count, swimming_pool_people_count
    )


def main():
    logging.info("Starting occupancy scraper")

    # Schedule the scraper to run every 10 minutes
    schedule.every().hour.at(":00").do(update_occupancy_data)
    schedule.every().hour.at(":10").do(update_occupancy_data)
    schedule.every().hour.at(":20").do(update_occupancy_data)
    schedule.every().hour.at(":30").do(update_occupancy_data)
    schedule.every().hour.at(":40").do(update_occupancy_data)
    schedule.every().hour.at(":50").do(update_occupancy_data)

    while True:
        try:
            schedule.run_pending()
            sleep(1)
        except KeyboardInterrupt:
            logging.info("Exiting occupancy scraper")
            break


if __name__ == "__main__":
    main()
