import pandas as pd
import json
import os

def normalize_raw_to_csv(period_start, period_end, **kwargs):
    """
    Нормализует JSON за указанный период в CSV.
    """
    start = period_start.split('T')[0]
    end = period_end.split('T')[0]
    
    raw_file = f"data/raw/variant_04/raw_{start}_{end}.json"
    norm_dir = 'data/normalized/variant_04/'
    os.makedirs(norm_dir, exist_ok=True)
    
    with open(raw_file, 'r') as f:
        data = json.load(f)
    
    hourly = data['hourly']
    df = pd.DataFrame(hourly)
    df['city_id'] = 'GB_LON'
    df.rename(columns={
        'temperature_2m': 'temp',
        'relative_humidity_2m': 'humidity',
        'precipitation': 'precip',
        'wind_speed_10m': 'windspeed'
    }, inplace=True)
    
    output_file = f"data/normalized/variant_04/normalized_{start}_{end}.csv"
    df.to_csv(output_file, index=False)
    print(f"Normalized {len(df)} rows → {output_file}")
    return {'rows': len(df), 'file': output_file}
