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
# Неделя 7 — Визуализация данных (Погода Лондон)

## Данные
- Файл: `data/mart/variant_04/mart_daily_*.csv`
- Поля: `date`, `avg_temp_c`, `max_temp_c`, `total_precip_mm`, `rainy_hours`, `max_wind_kmh`

## Типы графиков
| График | Что показывает |
|--------|----------------|
| Линейный (line) | Динамика температуры и осадков во времени |
| Гистограмма | Распределение среднесуточной температуры |
| Столбчатый | Топ дождливых / тёплых / ветреных дней |

## Техника
- `pandas` + `matplotlib` / `seaborn`
- `date` → `datetime`, сортировка по времени
- Подписи осей с единицами измерения (°C, мм, км/ч)
- Заголовки, легенда, сетка

## Выводы
1. Чёткая сезонность температуры (зима 0–5°C, лето до 30°C)
2. Осадки чаще <5 мм, экстремумы (>20 мм) редки
3. Распределение температур смещено в тёплую сторону
4. На временном ряду видны редкие аномалии

## Результаты
- `notebooks/week7_viz.ipynb`
- `docs/screenshots/week7/`
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
# Неделя 9 — Data Governance

## Часть 0. Ошибка единиц

### Проблема
```python
# Ошибка: лишнее умножение
precipitation_mm_wrong = precipitation_m * 1000 * 1000
```

### Решение
Используйте суффиксы в именах колонок для явного указания единиц измерения:
- `_c` — градусы Цельсия (°C)
- `_mm` — миллиметры (мм)
- `_kmh` — километры в час (км/ч)

Также создайте файл `data_dictionary.md` для документирования единиц измерения.

---

## Часть 1. Data Contract

**Версия:** 0.2

### Changelog
- 0.1 → 0.2: добавлены единицы измерения

### Правила
1. Используйте `snake_case` для имен колонок
2. Единицы измерения указываются в суффиксе имени колонки
3. Дата: поле `date`
4. Время: UTC

---

## Часть 2. Data Dictionary (mart)

| Колонка          | Единица |
|------------------|---------|
| `avg_temp_c`     | °C      |
| `max_temp_c`     | °C      |
| `total_precip_mm`| мм      |
| `rainy_hours`    | часы    |
| `max_wind_kmh`   | км/ч    |

---

## Файлы

- `docs/Data_Contract.md`
- `docs/data_dictionary.md`

# Неделя 10 — Docker + PostgreSQL + Metabase

## Используемые технологии
- Docker / Docker Compose
- PostgreSQL 15
- Metabase
- Python + pandas + SQLAlchemy

## Запуск проекта

```bash
docker compose up -d
docker compose ps
python src/load/load_incremental.py
```

## Подключения

| Сервис      | Адрес                     | Логин/пароль                        |
|-------------|---------------------------|-------------------------------------|
| PostgreSQL  | `localhost:5433`          | `airflow` / `airflow`               |
| Metabase    | [http://localhost:3000](http://localhost:8080/) | настраивается при первом входе |

## Docker Volumes

- `postgres_data` — данные БД
- `metabase_data` — настройки Metabase

## BI Dashboard

### Источник данных
`weather_london_daily_mart` (витрина погоды Лондон)

### Визуализации
- **Line chart** — динамика температуры
- **Bar chart** — топ дождливых дней
- **Summary** — средние показатели

### Скриншоты
`docs/bi/`
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

### Неделя 14: LLM-аналитика
Внедрен модуль автоматической интерпретации данных с использованием локальной LLM (Llama 3.1).
- **Реализация:** Интеграция через API Ollama.
- **Цель:** Автоматическое получение аналитических выводов по состоянию погоды без использования платных облачных API.
- **Результаты:** Генерация отчетов в формате `.md`, доступных в `docs/ml/llm_summary.md`.

