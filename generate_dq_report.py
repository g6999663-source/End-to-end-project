import json
import pandas as pd
import os

# Путь к вашему CSV файлу
csv_file = "/opt/airflow/data/mart/variant_04/mart_daily_2026-05-28_18-24-57.csv"

print(f"Чтение файла: {csv_file}")

# Читаем данные
df = pd.read_csv(csv_file)

print(f"Загружено строк: {len(df)}")
print(f"Колонки: {list(df.columns)}")

# Проверки качества данных
checks = {
    'no_nulls_date': df['date'].notna().all(),
    'no_nulls_avg_temp': df['avg_temp_c'].notna().all(),
    'no_nulls_max_temp': df['max_temp_c'].notna().all(),
    'temperature_range': df['avg_temp_c'].between(-20, 45).all(),
    'unique_dates': df['date'].is_unique,
    'positive_rain': (df['total_precip_mm'] >= 0).all(),
    'wind_range': df['max_wind_kmh'].between(0, 200).all(),
}

report = {
    'period': "2024-01-01 to 2024-01-31",
    'total_rows': len(df),
    'columns': list(df.columns),
    'checks': checks,
    'pass_count': sum(checks.values()),
    'fail_count': len(checks) - sum(checks.values()),
    'overall_status': "PASSED" if sum(checks.values()) == len(checks) else "FAILED"
}

# Сохраняем отчёт в корень
output_file = "dq_report.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✅ DQ отчёт сохранён в {output_file}")
print(f"Результат: {report['pass_count']} пройдено, {report['fail_count']} не пройдено")
print(f"Общий статус: {report['overall_status']}")

# Также сохраняем в папку docs (на всякий случай)
os.makedirs('docs', exist_ok=True)
with open('docs/dq_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("✅ Также сохранён в docs/dq_report.json")