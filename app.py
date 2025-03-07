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

app = Flask(__name__)

# Deaktiviert das Caching für die Antworten
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    return response

# Lade die JSON-Daten aus der Datei
def load_json_data():
    with open("occupancy_data/occupancy_data.json", "r") as file:
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

# Erzeugt ein Balkendiagramm und liefert es als Base64-kodierten String zurück
def create_bar_plot(hours, counts, title, color):
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 3), dpi=200)
    ax.bar(hours, counts, color=color)
    ax.set_title(title)
    ax.set_ylabel("Anzahl Besucher")
    ax.set_xlabel("Uhrzeit")
    plt.xticks(rotation=45)
    
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
    return create_bar_plot(hours, counts, "Keine Daten verfügbar", "grey")

# Generiert die Tagesplots (Balkendiagramme) und den Wochendurchschnittsplot
def generate_plots(selected_day, json_data, key, title, color):
    daily_data = json_data.get(selected_day, {})
    if not daily_data:
        return create_empty_plot(), create_empty_plot()
    
    # Tagesplot: Es werden nur die Stunden 08:00 bis 22:00 verwendet
    hours, values = get_hourly_data(daily_data, key)
    day_plot = create_bar_plot(hours, values, f"{title} am {selected_day}", color)
    
    # Wochendurchschnittsplot: Berechne für jeden Tag den Durchschnitt aller Werte des Schlüssels
    weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    weekday_occupancy = {day: [] for day in weekdays}
    
    for day, times in json_data.items():
        weekday = get_weekday_short(datetime.strptime(day, "%Y-%m-%d").strftime("%a"))
        # Durchschnitt aus allen 30-minütigen Werten des Tages
        avg_count = np.mean([t.get(key, 0) for t in times.values()])
        weekday_occupancy[weekday].append(avg_count)
    
    avg_occupancy = [np.mean(weekday_occupancy[d]) if weekday_occupancy[d] else 0 for d in weekdays]
    week_plot = create_bar_plot(weekdays, avg_occupancy, f"Durchschnittliche {title} pro Wochentag", color)
    
    return day_plot, week_plot

@app.route('/')
def index():
    selected_day = request.args.get('day', datetime.today().strftime('%Y-%m-%d'))
    selected_button = request.args.get('button', 'gym')
    
    json_data = load_json_data()
    # Stelle sicher, dass ein vorhandenes Datum genutzt wird
    selected_day_full = get_full_date_from_weekday(selected_day, json_data)
    
    if selected_button == 'swimmingPool':
        plot_url1, plot_url2 = generate_plots(selected_day_full, json_data, "pool_people_count", "Schwimmbad-Besucher", "blue")
    else:
        plot_url1, plot_url2 = generate_plots(selected_day_full, json_data, "fitness_room_people_count", "Gym-Besucher", "green")
    
    return render_template('index.html',
                           plot_url1=plot_url1,
                           plot_url2=plot_url2,
                           selected_day=selected_day,
                           selected_button=selected_button)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
