import json
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Serverseitiges Backend ohne GUI

import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request
from datetime import datetime
from typing import Dict, List

app = Flask(__name__)

OCCUPANCY_NOT_FOUND = -1

# Deaktiviert das Caching für die Antworten
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    return response

# Lade die JSON-Daten aus der Datei
def load_json_data():
    with open("occupancy_data/occupancy_data_example.json", "r") as file:
        return json.load(file)

# Funktion zur Umwandlung der englischen Wochentage in die HTML-kompatiblen Kürzel
def get_weekday_short(weekday):
    weekday_map = {
        "Mon": "Mo", "Tue": "Tu", "Wed": "We", "Thu": "Th",
        "Fri": "Fr", "Sat": "Sa", "Sun": "Su"
    }
    return weekday_map.get(weekday, "")

# Falls der übergebene Tag (z.B. 'Mo') nicht in den Daten vorkommt, wird das erste verfügbare Datum zurückgegeben
def get_full_date_from_weekday(selected_day, json_data):
    if selected_day in json_data:
        return selected_day
    # Wenn der Parameter zwei Zeichen lang ist, versuchen wir eine Übereinstimmung anhand des Wochentagskürzels
    if len(selected_day) == 2:
        matching_dates = [
            d for d in json_data.keys()
            if get_weekday_short(datetime.strptime(d, "%Y-%m-%d").strftime("%a")) == selected_day
        ]
        if matching_dates:
            return sorted(matching_dates)[0]
    # Fallback: Gib das erste Datum in den JSON-Daten zurück
    if json_data:
        return sorted(json_data.keys())[0]
    return selected_day

# Erzeugt eine Liste von Stunden (08:00 bis 22:00) und füllt fehlende Werte mit 0
def get_hourly_data(daily_data, key):
    hours = [f"{hour:02d}:00" for hour in range(8, 23)]
    counts = [daily_data.get(hour, {}).get(key, 0) for hour in hours]
    return hours, counts

# Create a list of 10-minute intervals from 08:00 to 22:00 and fill missing values with 0
def get_ten_minute_data(daily_data, key):
    times = [f"{hour:02d}:{minute:02d}" for hour in range(8, 22) for minute in range(0, 60, 10)]
    times.append("22:00")  # Ensure last entry is 22:00
    counts = [daily_data.get(time, {}).get(key, 0) for time in times]
    return times, counts

def create_bar_plot(times, counts, title, color):
    sns.set(style="white")
    fig, ax = plt.subplots(figsize=(8, 3), dpi=200)
    ax.bar(times, counts, color=color)
    ax.set_title(title)
    ax.set_ylabel("Visitor Count")
    ax.set_xlabel("Time")

    # Show only full hours on the x-axis
    full_hours = [time for time in times if time.endswith(":00")]
    indices = [times.index(hour) for hour in full_hours]
    ax.set_xticks(indices)
    ax.set_xticklabels(full_hours, rotation=45)

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# Erzeugt einen leeren Plot, falls für einen Tag keine Daten vorliegen
def create_empty_plot():
    hours = [f"{hour:02d}:00" for hour in range(8, 23)]
    counts = [0] * len(hours)
    return create_bar_plot(hours, counts, "No Data available", "grey")

def create_colored_bar_plot(times, counts, colors, primary_color, title):
    sns.set(style="white")
    fig, ax = plt.subplots(figsize=(14, 5), dpi=200)

    for i, time in enumerate(times):
        ax.bar(time, counts[i], color=colors[i])

    ax.set_title(title)
    ax.set_ylabel("Visitor Count")
    ax.set_xlabel("Time")
    ax.set_xticks(times[::6])  # Show only full-hour labels for clarity
    ax.set_xticklabels(times[::6], rotation=45)
    ax.grid(False)

    # Add legend
    handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=primary_color, markersize=10, label='Actual Data'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor="grey", markersize=10, label='No Data (Using Averages)')
    ]
    ax.legend(handles=handles, loc='upper right', title="Color Legend")

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def generate_daily_uccupany_plot(selected_day: str, json_data: dict, key: str, title: str, color: str):
    daily_data: Dict[str, Dict[str, int]] = json_data.get(selected_day, {})

    # Get the current time in HH:MM format
    current_time = datetime.now().strftime("%H:%M")

    # Generate time labels for every 10 minutes from 08:00 to 22:00
    times = [f"{hour:02d}:{minute:02d}" for hour in range(8, 22) for minute in range(0, 60, 10)]
    times.append("22:00")  # Ensure last entry is 22:00

    # Extract today's data for each 10-minute slot
    values = [daily_data.get(time, {}).get(key, OCCUPANCY_NOT_FOUND) for time in times]

    # Calculate averages for each 10-minute slot from past days
    weekday_occupancy = {time: [] for time in times}
    for times_data in json_data.values():
        times_data: Dict[str, Dict[str, int]]
        for time, occupancy_data in times_data.items():
            weekday_occupancy[time].append(occupancy_data.get(key))

    avg_occupancy_per_time = {time: np.mean(weekday_occupancy[time]) if weekday_occupancy[time] else 0 for time in times}

    # Assign colors: Green for past times, Grey for future times
    bar_colors = []
    for time in times:
        # Use actual data if available, otherwise use average
        if (time > current_time and selected_day == datetime.today().strftime("%Y-%m-%d")) or values[times.index(time)] == OCCUPANCY_NOT_FOUND:
            bar_colors.append("grey")
            values[times.index(time)] = avg_occupancy_per_time.get(time)  # Use average

        elif time <= current_time or selected_day != datetime.today().strftime("%Y-%m-%d"):
            bar_colors.append(color)  # Green for collected data

    # Create bar plot with color-coded bars
    day_plot = create_colored_bar_plot(times, values, bar_colors, color, f"{title} on {selected_day}")

    return day_plot

def generate_weekly_occupancy_plot(json_data: dict, key: str, title: str, color: str):
    # Define the days of the week (Monday to Sunday)
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Initialize a list to store the average occupancy for each day
    weekday_averages: List[List[float]] = [[] for _ in range(7)]

    for day in json_data:
        # Extract the daily data for the specified key (e.g., "fitness_room_people_count")
        daily_data:  Dict[str, Dict[str, int]] = json_data[day]
        daily_counts = [entry.get(key, 0) for entry in daily_data.values()]
        # Calculate the average occupancy for the day
        daily_avg = np.mean(daily_counts if daily_counts else [0])

        # Determine the index of the weekday (0: Monday, 1: Tuesday, ..., 6: Sunday)
        week_day_index = datetime.strptime(day, "%Y-%m-%d").weekday()
        weekday_averages[week_day_index].append(daily_avg)
    
    # Calculate the overall average occupancy for each day of the week
    daily_averages = [np.mean(occupancies) for occupancies in weekday_averages
                      if occupancies]

    sns.set(style="white")
    fig, ax = plt.subplots(figsize=(14, 5), dpi=200)

    for i, day in enumerate(days_of_week):
        ax.bar(day, daily_averages[i], color=color)

    ax.set_title(title)
    ax.set_ylabel("Visitor Average")
    ax.set_xlabel("Time")
    ax.set_xticks(days_of_week)  # Show only full-hour labels for clarity
    ax.set_xticklabels(days_of_week, rotation=45)
    ax.grid(False)

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url

@app.route('/')
def index():
    selected_day = request.args.get('day', datetime.today().strftime('%Y-%m-%d'))
    selected_button = request.args.get('button', 'gym')
    
    json_data = load_json_data()
    # Stelle sicher, dass ein vorhandenes Datum genutzt wird
    selected_day_full = get_full_date_from_weekday(selected_day, json_data)
    
    if selected_button == 'swimmingPool':
        plot_url1 = generate_daily_uccupany_plot(selected_day_full, json_data, "pool_people_count", "Pool-Visitors", "blue")
        plot_url2 = generate_weekly_occupancy_plot(json_data, "pool_people_count", "Pool-Visitors", "blue")
    else:
        plot_url1 = generate_daily_uccupany_plot(selected_day_full, json_data, "fitness_room_people_count", "Gym-Visitors", "green")
        plot_url2 = generate_weekly_occupancy_plot(json_data, "fitness_room_people_count", "Gym-Visitors", "green")
    
    return render_template('index.html',
                           plot_url1=plot_url1,
                           plot_url2=plot_url2,
                           selected_day=selected_day,
                           selected_button=selected_button)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
