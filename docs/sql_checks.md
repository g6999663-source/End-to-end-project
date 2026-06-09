# SQL checks для таблицы `weather_london_daily_mart` (variant_04, London)

## 1. Таблица не пустая

```sql
SELECT COUNT(*) AS row_count 
FROM weather_london_daily_mart;
```

**Ожидается:**  
> 0 (количество строк динамически растет по мере выполнения инкрементальных запусков Airflow DAG).

---

## 2. Диапазон дат

```sql
SELECT 
    MIN(date) AS min_date, 
    MAX(date) AS max_date 
FROM weather_london_daily_mart;
```

**Ожидается:**  
Даты находятся в пределах логического интервала сбора истории.  
Максимальная дата не должна превышать текущий день:  
`MAX(date) <= CURRENT_DATE`.

---

## 3. NULL в ключевых колонках

```sql
SELECT COUNT(*) AS null_count 
FROM weather_london_daily_mart
WHERE date IS NULL 
   OR city_id IS NULL;
```

**Ожидается:**  
0

---

## 4. Дубликаты по бизнес-ключу (date, city_id)

```sql
SELECT 
    date, 
    city_id, 
    COUNT(*) 
FROM weather_london_daily_mart
GROUP BY date, city_id
HAVING COUNT(*) > 1;
```

**Ожидается:**  
Пусто (0 строк)

---

## 5. Диапазон температур (разумные пределы)

```sql
SELECT 
    MIN(min_temp) AS global_min, 
    MAX(max_temp) AS global_max 
FROM weather_london_daily_mart;
```

**Ожидается:**  
Значения лежат в рамках физически возможных климатических границ для Лондона:  
`[-50.0, +60.0]`

---

## 6. Логика min ≤ avg ≤ max

```sql
SELECT COUNT(*) AS violations 
FROM weather_london_daily_mart
WHERE min_temp > avg_temp 
   OR avg_temp > max_temp;
```

**Ожидается:**  
0

---

## 7. Неотрицательные осадки

```sql
SELECT COUNT(*) 
FROM weather_london_daily_mart 
WHERE total_precip < 0;
```

**Ожидается:**  
0

---

## 8. Влажность в диапазоне [0, 100]

```sql
SELECT COUNT(*) 
FROM weather_london_daily_mart 
WHERE avg_humidity < 0 
   OR avg_humidity > 100;
```

**Ожидается:**  
0

---

## 9. Скорость ветра неотрицательна

```sql
SELECT COUNT(*) 
FROM weather_london_daily_mart 
WHERE avg_windspeed < 0;
```

**Ожидается:**  
0

---

## 10. Идемпотентность (хеш до и после повторного инкремента)

```sql
SELECT MD5(
    STRING_AGG(
        CONCAT(date, city_id, avg_temp, total_precip), 
        ',' 
        ORDER BY date
    )
) 
FROM weather_london_daily_mart;
```

**Ожидается:**  
Хеш-сумма состояния таблицы не изменяется при повторных тасках или ручных перезапусках (Clear Task Instance) в Airflow за один и тот же период благодаря транзакционной стратегии:

`DELETE period + INSERT`
> **Примечание:** Успешное выполнение данных SQL-проверок является обязательным условием (pre-requisite) для запуска ML-анализа аномалий. Если данные не проходят DQ-тесты, ML-пайплайн не должен обрабатывать «грязные» данные.