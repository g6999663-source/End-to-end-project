import pandas as pd
import os
from datetime import datetime

# ============================================================
# ОЖИДАЕМАЯ СХЕМА (из Data_Contract.md, версия 1.0)
# ============================================================
# Описание колонок mart-витрины:
# - name: имя колонки
# - dtype: ожидаемый тип данных pandas
# - nullable: допустимы ли NULL (False = обязательная)
# - description: краткое описание (для отчёта)

EXPECTED_SCHEMA = {
    "date": {
        "dtype": "datetime64[ns]",
        "nullable": False,
        "description": "Календарная дата"
    },
    "avg_temp": {
        "dtype": "float64",
        "nullable": False,
        "description": "Средняя температура за день, °C"
    },
    "min_temp": {
        "dtype": "float64",
        "nullable": False,
        "description": "Минимальная температура за день, °C"
    },
    "max_temp": {
        "dtype": "float64",
        "nullable": False,
        "description": "Максимальная температура за день, °C"
    },
    "avg_humidity": {
        "dtype": "float64",
        "nullable": False,
        "description": "Средняя влажность за день, %"
    },
    "total_precip": {
        "dtype": "float64",
        "nullable": False,
        "description": "Сумма осадков за день, мм"
    },
    "avg_windspeed": {
        "dtype": "float64",
        "nullable": False,
        "description": "Средняя скорость ветра за день, км/ч"
    },
    "city_id": {
        "dtype": "object",
        "nullable": False,
        "description": "Идентификатор города (GB_LON)"
    }
}

# Путь к mart-файлу (относительно корня проекта)
MART_PATH = "data/mart/variant_04/daily_weather.csv"

# ============================================================
# ФУНКЦИИ ПРОВЕРОК
# ============================================================

def load_data(file_path):
    """Загружает CSV и преобразует колонку date в datetime."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    df = pd.read_csv(file_path)

    # Преобразуем date в datetime, если это ещё не сделано
    if 'date' in df.columns and df['date'].dtype == 'object':
        df['date'] = pd.to_datetime(df['date'])

    return df

def check_columns_presence(df, expected_schema):
    """Проверяет, что все ожидаемые колонки присутствуют, и нет лишних."""
    actual_cols = set(df.columns)
    expected_cols = set(expected_schema.keys())

    missing = expected_cols - actual_cols
    extra = actual_cols - expected_cols

    return missing, extra

def check_column_types(df, expected_schema):
    """Проверяет типы данных каждой колонки."""
    type_issues = []
    for col, info in expected_schema.items():
        if col not in df.columns:
            continue
        actual_dtype = str(df[col].dtype)
        expected_dtype = info["dtype"]

        # Специальная обработка для datetime (может быть object до конвертации)
        if expected_dtype == "datetime64[ns]" and actual_dtype in ("object", "datetime64[ns]"):
            continue
        if actual_dtype != expected_dtype:
            type_issues.append({
                "column": col,
                "expected": expected_dtype,
                "actual": actual_dtype
            })
    return type_issues

def check_nullable(df, expected_schema):
    """Проверяет, что в обязательных колонках нет NULL."""
    null_violations = []
    for col, info in expected_schema.items():
        if col not in df.columns:
            continue
        if info["nullable"] == False:
            null_count = df[col].isna().sum()
            if null_count > 0:
                null_violations.append({
                    "column": col,
                    "null_count": null_count,
                    "total_rows": len(df)
                })
    return null_violations

def check_business_key_uniqueness(df):
    """Проверяет уникальность бизнес-ключа (date + city_id)."""
    duplicates = df.duplicated(subset=['date', 'city_id']).sum()
    return duplicates

def generate_report(df, missing, extra, type_issues, null_violations, duplicates):
    """Формирует и печатает отчёт, а также возвращает статус PASS/FAIL."""
    print("\n" + "="*70)
    print(" SCHEMA COMPLIANCE REPORT – variant_04 (London)")
    print("="*70)
    print(f"Файл: {MART_PATH}")
    print(f"Количество строк: {len(df)}")
    print(f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)

    # Статус
    has_fail = False

    # 1. Наличие колонок
    if missing:
        print(f" FAIL: Отсутствуют обязательные колонки: {', '.join(missing)}")
        has_fail = True
    else:
        print(" PASS: Все обязательные колонки присутствуют")

    if extra:
        print(f"⚠ WARNING: Обнаружены лишние колонки (не описанные в контракте): {', '.join(extra)}")
    else:
        print(" PASS: Лишних колонок нет")

    # 2. Типы данных
    if type_issues:
        print("\n FAIL: Несоответствие типов данных:")
        for issue in type_issues:
            print(f"   - {issue['column']}: ожидается {issue['expected']}, фактически {issue['actual']}")
        has_fail = True
    else:
        print("\n PASS: Типы данных соответствуют ожидаемым")

    # 3. NULL в обязательных колонках
    if null_violations:
        print("\n FAIL: NULL значения в обязательных колонках:")
        for issue in null_violations:
            print(f"   - {issue['column']}: {issue['null_count']} NULL из {issue['total_rows']} строк")
        has_fail = True
    else:
        print("\n PASS: Нет NULL в обязательных колонках")

    # 4. Уникальность бизнес-ключа
    if duplicates > 0:
        print(f"\n FAIL: Бизнес-ключ (date + city_id) не уникален – {duplicates} дубликатов")
        has_fail = True
    else:
        print("\n PASS: Бизнес-ключ уникален")

    # 5. Дополнительная проверка диапазона температур (quick sanity)
    if 'min_temp' in df.columns and 'max_temp' in df.columns:
        logical_violations = ((df['min_temp'] > df['max_temp'])).sum()
        if logical_violations > 0:
            print(f"\n⚠ WARNING: В {logical_violations} строках min_temp > max_temp (логическая ошибка)")

    print("="*70)
    if has_fail:
        print("ИТОГ:  SCHEMA CHECK FAILED – данные не соответствуют контракту")
    else:
        print("ИТОГ:  SCHEMA CHECK PASSED – данные полностью соответствуют контракту")
    print("="*70)

    return not has_fail

# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Запускает все проверки и возвращает exit code."""
    try:
        df = load_data(MART_PATH)
    except FileNotFoundError as e:
        print(f" Ошибка: {e}")
        return 1

    missing, extra = check_columns_presence(df, EXPECTED_SCHEMA)
    type_issues = check_column_types(df, EXPECTED_SCHEMA)
    null_violations = check_nullable(df, EXPECTED_SCHEMA)
    duplicates = check_business_key_uniqueness(df)

    success = generate_report(df, missing, extra, type_issues, null_violations, duplicates)

    return 0 if success else 1

# ============================================================
# ТОЧКА ВХОДА
# ============================================================
if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
