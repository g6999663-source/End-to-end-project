import pandas as pd
import os
from sqlalchemy import create_engine

def load_mart_to_postgres(period_start, period_end, postgres_conn_id=None, **kwargs):
    """
    Загружает mart в PostgreSQL с защитой от дублей.
    """
    start = period_start.split('T')[0]
    end = period_end.split('T')[0]
    
    mart_file = f"data/mart/variant_04/mart_{start}_{end}.csv"
    df = pd.read_csv(mart_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # Подключение к БД
    if postgres_conn_id:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        engine = hook.get_sqlalchemy_engine()
    else:
        engine = create_engine("postgresql://myuser:mysecretpassword@postgres:5432/mydb")
    
    # ИДЕМПОТЕНТНОСТЬ: удаляем данные за этот период перед вставкой
    with engine.begin() as conn:
        conn.execute(f"DELETE FROM daily_weather WHERE date >= '{start}' AND date <= '{end}'")
    
    # Вставляем новые данные
    df.to_sql('daily_weather', engine, if_exists='append', index=False)
    print(f"Loaded {len(df)} rows for period {start} → {end}")
    
    return {'loaded_rows': len(df)}
