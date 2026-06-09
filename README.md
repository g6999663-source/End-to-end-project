# Сквозной проект (End-to-End Data Engineering)

Учебный end-to-end проект по дата-инженерии: автоматическое получение метеорологических данных через Open-Meteo API, нормализация, построение суточной аналитической витрины (mart), проверки качества данных (Data Quality Gate), загрузка в PostgreSQL и Airflow-оркестрация.

---

## Что делает проект

Проект работает с историческими и оперативными погодными данными по городу Лондон (Великобритания).

Основная цепочка:
**Extract ➔ Transform ➔ Mart ➔ DQ ➔ Load**

---

## Слои данных

- `data/raw/variant_04/` — raw JSON из Open-Meteo API  
- `data/normalized/variant_04/` — очищенные CSV  
- `data/mart/variant_04/` — аналитическая витрина  
- `docs/dq_report.json` — отчет качества данных  

---

## Быстрый запуск проекта

### Запуск инфраструктуры

```bash
docker compose up -d
```

### Полный запуск (Full mode)

```bash
python -m src.pipeline.pipeline --mode full
```

### Инкрементальный запуск (Incremental mode)

```bash
python -m src.pipeline.pipeline --mode incremental
```

### Airflow

- UI: http://localhost:8080  
- Логин/пароль: `airflow / airflow`  
- DAG: `weather_london_etl`

Цепочка задач: extract_weather ➔ normalize_data ➔ build_mart ➔ data_quality_checks ➔ load_to_postgres

---

## Источник данных

- Источник: Open-Meteo API  
- Локация: Лондон, Великобритания (`GB_LON`)  
- Конфигурация:
  - `configs/variant_04.yml`
  - `configs/cities.csv`

---

## Неделя 1 — Окружение

### Установка (Windows)

- Установить Miniconda / Python 3.11  
- Запустить:

```bash
scripts\setup_env.bat
```

### Smoke Test

При успешном запуске: [OK]

---

## Неделя 2 — Extract (API)

### Запуск

```bash
pip install requests pyyaml
python src/extract/extract_incremental.py
```

### Результат
data/raw/variant_04/raw_YYYYMMDD_HHMMSS.json

### Особенности

- Таймауты на HTTP-запросы  
- Логирование ошибок  
- JSON сохраняется без изменений  

---

## Неделя 3 — Transform (Pandas)

### Что сделано

- Раскрытие JSON через `pd.json_normalize`
- Приведение к табличному виду
- Очистка данных:
  - snake_case колонки
  - datetime типы
  - float/int приведение
  - удаление дубликатов и пропусков

### Зерно данных

1 строка = 1 час наблюдений

### Результат
data/normalized/variant_04/YYYY-MM-DD_HH-MM-SS.csv

---

## Неделя 4 — Data Mart

### KPI

- `avg_temp` — средняя температура  
- `min_temp / max_temp` — минимум / максимум  
- `avg_humidity` — средняя влажность  
- `total_precip` — сумма осадков  
- `avg_windspeed` — средний ветер  

### Запуск

```bash
python src/transform/build_mart.py
```

### Результат
data/mart/variant_04/

---

## Неделя 5 — PostgreSQL

### Что сделано

- Таблица: `weather_london_daily_mart`
- Идемпотентная загрузка
- SQL-проверки (5 тестов)

### Файлы

- `src/load/load_incremental.py`
- `src/sql_checks.py`
- `docs/sql_checks.md`

### Запуск

```bash
docker run -d --name postgres_db \
  -e POSTGRES_USER=airflow \
  -e POSTGRES_PASSWORD=airflow \
  -e POSTGRES_DB=airflow \
  -p 5434:5432 postgres:13

python src/load/load_incremental.py
python src/sql_checks.py
```

---

## Неделя 6 — ETL Pipeline

### Режимы

- Full — полная пересборка (TRUNCATE)
- Incremental — по watermark

### Запуск

```bash
python src/pipeline/pipeline.py --mode full
python src/pipeline/pipeline.py --mode incremental
```

### State Management
data/state.json

### Watermark

- Поле: `date`
- Уникальный ключ: `city_id + date`

---

## Неделя 8 — Data Quality

### Модуль

### Watermark

- Поле: `date`
- Уникальный ключ: `city_id + date`

---

## Неделя 8 — Data Quality

### Модуль
src/dq.py

### Проверки

- `non_empty` — не пустой датасет (FAIL)
- `not_null_date` — дата не NULL (FAIL)
- `unique_city_date` — уникальность (FAIL)
- `temperature_range` — диапазон [-50, 60] (FAIL)
- `precipitation_range` — >= 0 (FAIL)
- `wind_speed_limit` — выбросы (WARNING)

### Запуск

```bash
python src/dq.py
pytest tests/test_dq.py
```

### Отчет
docs/dq_report.json

---

## Неделя 11–12 — Docker + Airflow

### Архитектура

- PostgreSQL 13 (метабаза + хранилище)
- Airflow (Webserver + Scheduler)

### Инкрементальность

Используются Airflow-переменные:

{{ data_interval_start }}

{{ data_interval_end }}


Файлы: 

mart_YYYY-MM-DD.csv

### Идемпотентность

Стратегия:

DELETE + INSERT


### DQ Gate

- DQ встроен перед загрузкой
- FAIL → пайплайн останавливается
## Неделя 13 — ML-слой (Детекция аномалий)

Добавлен модуль интеллектуального анализа данных для выявления экстремальных климатических событий и технических сбоев.

### Реализованный функционал
- **Модель:** `IsolationForest` (Unsupervised Learning) для поиска аномалий.
- **Признаки:** `max_temp`, `total_precip`.
- **Защита от Leakage:** Использованы изолированные `Pipeline` (StandardScaler + Model).
- **Результаты:**
  - Генерация отчета `docs/ml/week13_summary.md`.
  - Выгрузка топ-аномалий в `docs/ml/anomalies_top.csv`.
  - Визуализация `docs/ml/metrics.png` (график с выделенными красным цветом аномалиями).

### Запуск анализа
Анализ выполняется через Jupyter Notebook:
`notebooks/week13_ml.ipynb`

---

## Инфраструктура и пайплайн

### Основные команды запуска
- **Инфраструктура:** `docker compose up -d`
- **Full ETL:** `python -m src.pipeline.pipeline --mode full`
- **Incremental ETL:** `python -m src.pipeline.pipeline --mode incremental`

### Airflow
- **UI:** http://localhost:8080
- **DAG:** `weather_london_etl`
- **DQ Gate:** Пайплайн автоматически прерывается при нарушении критериев качества (FAIL) перед загрузкой.

---

## Краткий обзор этапов

| Неделя | Этап | Ключевой артефакт |
| :--- | :--- | :--- |
| 1-2 | Extract | `data/raw/*.json` |
| 3-4 | Transform/Mart | `data/mart/*.csv` |
| 5-6 | Load/Pipeline | Postgres tables |
| 8 | DQ Checks | `docs/dq_report.json` |
| 11-12 | Airflow | ETL DAG |
| 13 | ML Analysis | `docs/ml/*` |

---

## Технологический стек
- **Язык:** Python 3.11
- **Оркестрация:** Apache Airflow
- **Хранилище:** PostgreSQL 13
- **Обработка:** Pandas, Scikit-learn
- **API:** Open-Meteo

