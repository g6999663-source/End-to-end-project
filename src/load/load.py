import pandas as pd
import os
import glob
from sqlalchemy import create_engine, text
from datetime import datetime

# Параметры подключения
DB_USER = "myuser"
DB_PASSWORD = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mydb"
TABLE_NAME = "mart_variant_04_daily"

# Поиск последнего mart-файла
mart_dir = "data/mart/variant_04/"
list_of_files = glob.glob(mart_dir + "mart_daily_*.csv")
if not list_of_files:
    raise FileNotFoundError(f"Нет mart-файлов в {mart_dir}")

latest_file = max(list_of_files, key=os.path.getctime)
print(f"[INFO] Загружаем файл: {latest_file}")

# Чтение CSV
df = pd.read_csv(latest_file)
print(f"[INFO] Формат: {df.shape[0]} строк, {df.shape[1]} столбцов")
print("[INFO] Колонки:", list(df.columns))

# Приведение даты к datetime
df['date'] = pd.to_datetime(df['date'])

# Подключение к Postgres и загрузка (идемпотентно: пересоздаём таблицу)
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

with engine.begin() as conn:
    # Удаляем старую таблицу, если есть
    conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME}"))
    print(f"[INFO] Таблица {TABLE_NAME} удалена (если существовала).")
    # Загружаем данные
    df.to_sql(TABLE_NAME, conn, index=False, if_exists='replace')
    print(f"[INFO] Таблица {TABLE_NAME} создана, загружено {len(df)} строк.")

# Проверка после загрузки
with engine.connect() as conn:
    count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).fetchone()[0]
    print(f"[OK] Итоговое количество строк в таблице: {count}")
