import json
from time import sleep
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup


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


def save_occupancy_data(update_time: str, fitness_room_people_count: int, swimming_pool_people_count: int) -> None:
    # Prepare the data entry
    data_entry = {
        "fitness_room_people_count": fitness_room_people_count,  
        "pool_people_count": swimming_pool_people_count           
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
        print(f"Data for {update_day} at {update_time} already exists")
        return

    # Store data with timestamp
    all_data[update_day][update_time] = data_entry

    # Write the updated data back to the JSON file
    with open("occupancy_data/occupancy_data.json", "w") as file:
        json.dump(all_data, file)

def update_occupancy_data():
    people_counts, update_time = fetch_occupancy()

    if len(people_counts) == 0:
        print("No occupancy data available")
        return

    if update_time == "N/A":
        print("No update time available")
        return

    fitness_room_people_count: int = people_counts[0]
    swimming_pool_people_count: int = people_counts[3]

    save_occupancy_data(update_time, fitness_room_people_count, swimming_pool_people_count)

def main():
    while True:
        try:
            update_occupancy_data()
            sleep(5)
        except KeyboardInterrupt:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
