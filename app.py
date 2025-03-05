import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import base64
from flask import Flask, render_template, request

app = Flask(__name__)

def generate_gym_plots(selected_day):
    # Beispiel-Daten für das Balkendiagramm für das Gym
    categories = ['Geräte', 'Kurse', 'Freihantelbereich', 'Cardio']
    values = np.random.randint(10, 100, size=len(categories))
    
    # Erstellen des Balkendiagramms mit Seaborn
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 3), dpi=200)
    sns.barplot(x=categories, y=values, palette='viridis', ax=ax)
    ax.set_title(f'Nutzung am {selected_day}')
    ax.set_ylabel('Anzahl Besucher')
    
    # Speichern des Balkendiagramms als Base64
    img1 = io.BytesIO()
    plt.savefig(img1, format='png', bbox_inches='tight')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()
    plt.close()
    
    # Beispiel-Daten für die Wochentagsauslastung
    days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    occupancy = np.random.randint(20, 100, size=len(days))
    
    # Erstellen des Linienplots mit Seaborn
    fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
    sns.lineplot(x=days, y=occupancy, marker='o', linestyle='-', color='orange', ax=ax)
    ax.set_title('Auslastung pro Wochentag')
    ax.set_ylabel('Belegungsgrad (%)')
    ax.set_xlabel('Wochentage')
    
    # Speichern des Linienplots als Base64
    img2 = io.BytesIO()
    plt.savefig(img2, format='png', bbox_inches='tight')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()
    plt.close()
    
    return plot_url1, plot_url2

def generate_swimming_pool_plots(selected_day):
    # Beispiel-Daten für das Balkendiagramm für die Schwimmhalle
    categories = ['Bahnen 1-3', 'Bahnen 4-6', 'Sprungbecken', 'Kinderbecken']
    values = np.random.randint(10, 100, size=len(categories))
    
    # Erstellen des Balkendiagramms mit Seaborn
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 3), dpi=200)
    sns.barplot(x=categories, y=values, palette='Blues', ax=ax)
    ax.set_title(f'Nutzung am {selected_day} (Schwimmhalle)')
    ax.set_ylabel('Anzahl Besucher')
    
    # Speichern des Balkendiagramms als Base64
    img1 = io.BytesIO()
    plt.savefig(img1, format='png', bbox_inches='tight')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()
    plt.close()
    
    # Beispiel-Daten für die Wochentagsauslastung der Schwimmhalle
    days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    occupancy = np.random.randint(20, 100, size=len(days))
    
    # Erstellen des Linienplots mit Seaborn
    fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
    sns.lineplot(x=days, y=occupancy, marker='o', linestyle='-', color='blue', ax=ax)
    ax.set_title('Auslastung pro Wochentag (Schwimmhalle)')
    ax.set_ylabel('Belegungsgrad (%)')
    ax.set_xlabel('Wochentage')
    
    # Speichern des Linienplots als Base64
    img2 = io.BytesIO()
    plt.savefig(img2, format='png', bbox_inches='tight')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()
    plt.close()
    
    return plot_url1, plot_url2

@app.route('/')
def index():
    selected_day = request.args.get('day', 'Mo')  # Standardwert 'Mo'
    selected_button = request.args.get('button', 'gym')  # Standardmäßig 'gym'
    
    if selected_button == 'swimmingPool':
        plot_url1, plot_url2 = generate_swimming_pool_plots(selected_day)
    else:
        plot_url1, plot_url2 = generate_gym_plots(selected_day)
    
    return render_template('index.html', plot_url1=plot_url1, plot_url2=plot_url2, selected_day=selected_day, selected_button=selected_button)

if __name__ == '__main__':
    app.run(debug=True)
