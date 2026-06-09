import os
import json
import requests
from datetime import datetime

def extract_weather_data(period_start, period_end, **kwargs):
    """
    Загружает данные из Open-Meteo API за указанный период.
    """
    # Конвертируем строки в объекты date
    start = datetime.fromisoformat(period_start.replace('T', ' ')).date()
    end = datetime.fromisoformat(period_end.replace('T', ' ')).date()
    
    print(f"Extracting for period: {start} → {end}")
    
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude=51.5074&longitude=-0.1278&start_date={start}&end_date={end}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
    
    response = requests.get(url)
    data = response.json()
    
    # Сохраняем raw с привязкой к периоду
    os.makedirs('data/raw/variant_04', exist_ok=True)
    filename = f"data/raw/variant_04/raw_{start}_{end}.json"
    with open(filename, 'w') as f:
        json.dump(data, f)
    
    print(f"Saved: {filename}")
    return {'file': filename, 'rows': len(data.get('hourly', {}).get('time', []))}
