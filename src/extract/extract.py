import requests
import json
import yaml
import os
from datetime import datetime

# ============================================
# 1. ЗАГРУЗКА ТВОЕГО КОНФИГА (variant_04.yml)
# ============================================

config_path = "configs/variant_04.yml"

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Достаем данные из конфига
variant_id = config["variant_id"]
source_type = config["source_type"]
entity = config["entity"]
base_url = config["api"]["base_url"]
params = config["api"]["params"]

print(f"[INFO] Вариант: {variant_id}")
print(f"[INFO] Тема: {config['theme']}")
print(f"[INFO] Город: {entity['city_name']} ({entity['city_id']})")
print(f"[INFO] Координаты: широта {entity['latitude']}, долгота {entity['longitude']}")
print(f"[INFO] URL: {base_url}")

# ============================================
# 2. ДОБАВЛЯЕМ ДАТЫ (обязательно для archive API)
# ============================================

# Archive API требует параметры start_date и end_date
# Укажи нужные даты (можно поменять)
params["start_date"] = "2024-01-01"
params["end_date"] = "2024-01-07"

print(f"[INFO] Период: {params['start_date']} по {params['end_date']}")
print(f"[INFO] Часовые данные: {params['hourly']}")

# ============================================
# 3. ВЫПОЛНЕНИЕ ЗАПРОСА
# ============================================

timeout_sec = 15

try:
    response = requests.get(base_url, params=params, timeout=timeout_sec)
    response.raise_for_status()
    data = response.json()
    
    print(f"[INFO] HTTP Статус: {response.status_code}")
    
    # Проверяем, есть ли данные
    if "hourly" in data:
        print(f"[INFO] Найдено часовых записей: {len(data['hourly']['time'])}")
    else:
        print("[WARNING] В ответе нет поля 'hourly'")

# ============================================
# 4. ОБРАБОТКА ОШИБОК
# ============================================

except requests.exceptions.Timeout:
    print(f"[ERROR] Таймаут! Сервер не ответил за {timeout_sec} секунд.")
    exit(1)
    
except requests.exceptions.ConnectionError:
    print("[ERROR] Ошибка соединения. Проверьте интернет.")
    exit(1)
    
except requests.exceptions.HTTPError as e:
    print(f"[ERROR] HTTP ошибка: {e.response.status_code}")
    if e.response.status_code == 400:
        print("   Проверьте правильность дат (start_date, end_date)")
    exit(1)
    
except json.JSONDecodeError:
    print("[ERROR] Ответ сервера не является JSON.")
    exit(1)
    
except Exception as e:
    print(f"[ERROR] Неизвестная ошибка: {e}")
    exit(1)

# ============================================
# 5. СОХРАНЕНИЕ JSON ФАЙЛА
# ============================================

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"{timestamp}.json"

# Путь: data/raw/variant_04/2024-01-01_2024-01-07_2026-03-10_15-42-11.json
# (добавляем период в имя файла для удобства)
period = f"{params['start_date']}_{params['end_date']}"
filename_with_period = f"{period}_{timestamp}.json"

output_dir = f"data/raw/variant_{variant_id}"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, filename_with_period)

# Сохраняем JSON
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[INFO] Данные сохранены: {output_path}")
print(f"[INFO] Размер файла: {os.path.getsize(output_path)} байт")

# ============================================
# 6. КРАТКИЙ ЛОГ (что нужно по заданию)
# ============================================

print("\n=== SUMMARY ===")
print(f"Вариант: {variant_id}")
print(f"Источник: {source_type}")
print(f"Город: {entity['city_name']}")
print(f"Период: {params['start_date']} - {params['end_date']}")
print(f"URL: {base_url}")
print(f"Статус: {response.status_code}")
print(f"Сохранено: {output_path}")
print(f"Количество записей: {len(data.get('hourly', {}).get('time', []))}")
print("[OK] Извлечение данных завершено успешно!")
