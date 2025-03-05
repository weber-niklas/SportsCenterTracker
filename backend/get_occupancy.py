import csv
import os
from time import sleep
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

def ensure_csv_exists():
    filename = "C:/Users/tomha/OneDrive/Desktop/Taiwan/gym_website/occupancy_data/occupancy_data/occupancy_data.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not os.path.exists(filename):
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Update Time", "Occupancy", "People Training"])

def fetch_occupancy() -> Tuple[List[int], str]:
    url: str = "https://rent.pe.ntu.edu.tw/"
    headers: str = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    people_counts: List[str] = [span.text.strip() for span in soup.select(".ICI span")][:3]
    people_counts: List[int] = [int(count) for count in people_counts if count.isdigit()]
    update_time: str = (
        soup.select_one(".CMCUpTime").text.strip().split(" ")[1:]
        if soup.select_one(".CMCUpTime")
        else "N/A"
    )
    return people_counts, update_time

def save_occupancy_data(update_time: str, occupancy: float, people_training: int):
    ensure_csv_exists()
    with open("C:/Users/tomha/OneDrive/Desktop/Taiwan/gym_website/occupancy_data/occupancy_data/occupancy_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([f"{update_time[0]} {update_time[1]}", f"{occupancy:.2f}%", people_training])

def read_occupancy_data() -> Tuple[List[str], List[float], List[int]]:
    ensure_csv_exists()
    update_times: List[str] = []
    occupancies: List[float] = []
    people_trainings: List[int] = []
    with open("./occupancy_data/occupancy_data.csv", mode="r") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            update_times.append(row[0])
            occupancies.append(float(row[1].replace("%", "")))
            people_trainings.append(int(row[2]))
    return update_times, occupancies, people_trainings

def clear_occupancy_data():
    ensure_csv_exists()
    with open("./occupancy_data/occupancy_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Update Time", "Occupancy", "People Training"])

def update_occupancy_data():
    people_counts, update_time = fetch_occupancy()
    if len(people_counts) == 0 or update_time == "N/A":
        print("No valid occupancy data available")
        return
    people_currently_training: int = people_counts[0]
    people_capacity: int = people_counts[2]
    occupancy = people_currently_training / people_capacity * 100
    save_occupancy_data(update_time, occupancy, people_currently_training)

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