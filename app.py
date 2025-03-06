import json
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Setzt das Backend auf 'Agg' für serverseitige Nutzung

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
        "Mon": "Mo",
        "Tue": "Tu",
        "Wed": "We",
        "Thu": "Th",
        "Fri": "Fr",
        "Sat": "Sa",
        "Sun": "Su"
    }
    return weekday_map.get(weekday, "")

# Hilfsfunktion: Falls der ausgewählte Tag ein Wochentagskürzel ist, in einen vollen Datumseintrag umwandeln
def get_full_date_from_weekday(selected_day, json_data):
    # Wenn selected_day nicht als Schlüssel existiert und genau 2 Zeichen hat, dann suchen wir nach einem passenden Datum
    if selected_day not in json_data and len(selected_day) == 2:
        matching_dates = [
            d for d in json_data.keys()
            if get_weekday_short(datetime.strptime(d, "%Y-%m-%d").strftime("%a")) == selected_day
        ]
        if matching_dates:
            return sorted(matching_dates)[0]  # Nimm das früheste Datum
    return selected_day

# Funktion zum Erstellen eines leeren Diagramms
def create_empty_plot():
    fig, ax = plt.subplots(figsize=(8, 3), dpi=200)
    ax.set_title('Keine Daten verfügbar')
    ax.set_xlabel('Uhrzeit')
    ax.set_ylabel('Anzahl Besucher')
    ax.plot([], [])  # Leeres Diagramm
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# Funktion zum Generieren der Gym-Plots aus der JSON-Datei
def generate_gym_plots(selected_day, json_data):
    daily_data = json_data.get(selected_day, {})

    # Falls keine Daten für den Tag existieren, ein leeres Diagramm zurückgeben
    if not daily_data:
        return create_empty_plot(), create_empty_plot()

    # Besucherdaten auslesen
    timestamps = sorted(daily_data.keys())
    fitness_counts = [daily_data[t]["fitness_room_people_count"] for t in timestamps]

    # Plot für Gym-Besucherzahlen über den Tag
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 3), dpi=200)
    sns.lineplot(x=timestamps, y=fitness_counts, marker='o', linestyle='-', color='green', ax=ax)
    ax.set_title(f'Gym-Besucher am {selected_day}')
    ax.set_ylabel('Anzahl Besucher')
    ax.set_xlabel('Uhrzeit')
    plt.xticks(rotation=45)

    # Speichern als Base64
    img1 = io.BytesIO()
    plt.savefig(img1, format='png', bbox_inches='tight')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    # Wochendurchschnitt berechnen
    weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    weekday_occupancy = {day: [] for day in weekdays}

    for day, times in json_data.items():
        weekday = get_weekday_short(datetime.strptime(day, "%Y-%m-%d").strftime("%a"))
        avg_count = np.mean([t["fitness_room_people_count"] for t in times.values()])
        weekday_occupancy[weekday].append(avg_count)

    avg_occupancy = [np.mean(weekday_occupancy[d]) if weekday_occupancy[d] else 0 for d in weekdays]

    # Plot für durchschnittliche Auslastung pro Wochentag
    fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
    sns.lineplot(x=weekdays, y=avg_occupancy, marker='o', linestyle='-', color='orange', ax=ax)
    ax.set_title('Durchschnittliche Gym-Auslastung pro Wochentag')
    ax.set_ylabel('Durchschnitt Besucherzahl')
    ax.set_xlabel('Wochentage')

    # Speichern als Base64
    img2 = io.BytesIO()
    plt.savefig(img2, format='png', bbox_inches='tight')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()
    plt.close()

    return plot_url1, plot_url2

# Funktion für Swimming-Pool-Plots
def generate_swimming_pool_plots(selected_day, json_data):
    daily_data = json_data.get(selected_day, {})

    # Falls keine Daten für den Tag existieren, ein leeres Diagramm zurückgeben
    if not daily_data:
        return create_empty_plot(), create_empty_plot()

    # Besucherdaten auslesen
    timestamps = sorted(daily_data.keys())
    pool_counts = [daily_data[t]["pool_people_count"] for t in timestamps]

    # Plot für Pool-Besucherzahlen über den Tag
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 3), dpi=200)
    sns.lineplot(x=timestamps, y=pool_counts, marker='o', linestyle='-', color='blue', ax=ax)
    ax.set_title(f'Schwimmbad-Besucher am {selected_day}')
    ax.set_ylabel('Anzahl Besucher')
    ax.set_xlabel('Uhrzeit')
    plt.xticks(rotation=45)

    # Speichern als Base64
    img1 = io.BytesIO()
    plt.savefig(img1, format='png', bbox_inches='tight')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    # Wochendurchschnitt berechnen
    weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    weekday_occupancy = {day: [] for day in weekdays}

    for day, times in json_data.items():
        weekday = get_weekday_short(datetime.strptime(day, "%Y-%m-%d").strftime("%a"))
        avg_count = np.mean([t["pool_people_count"] for t in times.values()])
        weekday_occupancy[weekday].append(avg_count)

    avg_occupancy = [np.mean(weekday_occupancy[d]) if weekday_occupancy[d] else 0 for d in weekdays]

    # Plot für durchschnittliche Pool-Auslastung pro Wochentag
    fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
    sns.lineplot(x=weekdays, y=avg_occupancy, marker='o', linestyle='-', color='blue', ax=ax)
    ax.set_title('Durchschnittliche Schwimmbad-Auslastung pro Wochentag')
    ax.set_ylabel('Durchschnitt Besucherzahl')
    ax.set_xlabel('Wochentage')

    # Speichern als Base64
    img2 = io.BytesIO()
    plt.savefig(img2, format='png', bbox_inches='tight')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()
    plt.close()

    return plot_url1, plot_url2

# Flask-Route für die Webseite
@app.route('/')
def index():
    # Parameter holen; Standard ist heutiges Datum (im Format YYYY-MM-DD)
    selected_day = request.args.get('day', datetime.today().strftime('%Y-%m-%d'))
    selected_button = request.args.get('button', 'gym')

    json_data = load_json_data()

    # Falls der ausgewählte Tag ein Wochentagskürzel ist, in einen vollen Datumseintrag umwandeln
    selected_day_full = get_full_date_from_weekday(selected_day, json_data)

    if selected_button == 'swimmingPool':
        plot_url1, plot_url2 = generate_swimming_pool_plots(selected_day_full, json_data)
    else:
        plot_url1, plot_url2 = generate_gym_plots(selected_day_full, json_data)

    return render_template('index.html',
                           plot_url1=plot_url1,
                           plot_url2=plot_url2,
                           selected_day=selected_day,
                           selected_button=selected_button)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
