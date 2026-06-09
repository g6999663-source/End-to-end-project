import pandas as pd
import os

def build_daily_mart(period_start, period_end, **kwargs):
    """
    Строит суточную витрину из почасовых данных.
    """
    start = period_start.split('T')[0]
    end = period_end.split('T')[0]
    
    norm_file = f"data/normalized/variant_04/normalized_{start}_{end}.csv"
    mart_dir = 'data/mart/variant_04/'
    os.makedirs(mart_dir, exist_ok=True)
    
    df = pd.read_csv(norm_file)
    df['time'] = pd.to_datetime(df['time'])
    df['date'] = df['time'].dt.date
    
    daily = df.groupby('date').agg(
        avg_temp=('temp', 'mean'),
        min_temp=('temp', 'min'),
        max_temp=('temp', 'max'),
        avg_humidity=('humidity', 'mean'),
        total_precip=('precip', 'sum'),
        avg_windspeed=('windspeed', 'mean')
    ).reset_index()
    daily['city_id'] = 'GB_LON'
    daily['date'] = pd.to_datetime(daily['date'])
    
    output_file = f"data/mart/variant_04/mart_{start}_{end}.csv"
    daily.to_csv(output_file, index=False)
    print(f"Mart built: {len(daily)} rows → {output_file}")
    return {'rows': len(daily), 'file': output_file}
