from datetime import datetime, timedelta
import random
import json

# Define gym and pool capacity
max_gym = 181
max_pool = 50

# Define opening hours and time intervals
opening_time = 8  # 8 AM
closing_time = 22  # 10 PM
interval_minutes = 10

# Generate dates for the current week (Monday to Sunday)
today = datetime.today()
start_of_week = today - timedelta(days=today.weekday())  # Monday
week_dates = [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

# Generate sample data
data = {}
for date in week_dates:
    current_time = datetime.strptime(f"{opening_time}:00", "%H:%M")
    end_time = datetime.strptime(f"{closing_time}:00", "%H:%M")
    
    daily_data = {}
    while current_time <= end_time:
        time_str = current_time.strftime("%H:%M")
        daily_data[time_str] = {
            "fitness_room_people_count": random.randint(0, max_gym),
            "pool_people_count": random.randint(0, max_pool)
        }
        current_time += timedelta(minutes=interval_minutes)
    
    data[date] = daily_data

# Convert to JSON format
json_data = json.dumps(data, indent=4)

# Write to file
with open("occupancy_data/occupancy_data_example.json", "w") as file:
    file.write(json_data)
