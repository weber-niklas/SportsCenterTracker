import csv
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

    people_counts: List[str] = people_counts[
        :3
    ]  # Only first three numbers are for fitness center

    people_counts: List[int] = [
        int(count) for count in people_counts if count.isdigit()
    ]

    update_time: str = (
        soup.select_one(".CMCUpTime").text.strip().split(" ")[1:]
        if soup.select_one(".CMCUpTime")
        else "N/A"
    )

    return people_counts, update_time


def save_occupancy_data(update_time: str, occupancy: float, people_training: int):
    with open("./occupancy_data/occupancy_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)

        # If file is empty, write header
        if file.tell() == 0:
            writer.writerow(["Update Time", "Occupancy", "People Training"])

        # Write the occupancy data
        writer.writerow(
            [f"{update_time[0]} {update_time[1]}", f"{occupancy:.2f}%", people_training]
        )


def read_occupancy_data() -> Tuple[List[str], List[float], List[int]]:
    update_times: List[str] = []
    occupancies: List[float] = []
    people_trainings: List[int] = []

    with open("./occupancy_data/occupancy_data.csv", mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if reader.line_num == 1:
                continue
            update_times.append(row[0])
            occupancies.append(float(row[1].replace("%", "")))
            people_trainings.append(int(row[2]))

    return update_times, occupancies, people_trainings


def clear_occupancy_data():
    with open("./occupancy_data/occupancy_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Update Time", "Occupancy", "People Training"])

def update_occupancy_data():
    people_counts, update_time = fetch_occupancy()

    if len(people_counts) == 0:
        print("No occupancy data available")
        return

    if update_time == "N/A":
        print("No update time available")
        return

    people_currently_trainig: int = people_counts[0]
    people_capacity: int = people_counts[2]
    occupancy = people_currently_trainig / people_capacity * 100

    save_occupancy_data(update_time, occupancy, people_currently_trainig)

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
