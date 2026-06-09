"""
Unit-тесты для DQ-модуля
Запуск: pytest tests/
"""

import pytest
import pandas as pd
import sys
import os

# Добавляем путь к src для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dq import (
    check_table_not_empty,
    check_no_null_in_key,
    check_unique_business_key,
    check_temperature_range,
    check_non_negative_precipitation,
    check_humidity_range,
    check_temp_min_max_logic
)

# ========== Fixtures ==========

@pytest.fixture
def good_dataframe():
    """Корректный DataFrame для тестов"""
    return pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        'city_id': ['GB_LON', 'GB_LON', 'GB_LON'],
        'avg_temp': [5.0, 6.0, 7.0],
        'min_temp': [3.0, 4.0, 5.0],
        'max_temp': [7.0, 8.0, 9.0],
        'total_precip': [0.0, 2.5, 1.0],
        'avg_humidity': [75, 80, 70]
    })

@pytest.fixture
def empty_dataframe():
    """Пустой DataFrame"""
    return pd.DataFrame()

@pytest.fixture
def null_in_key_dataframe():
    """DataFrame с NULL в ключевых полях"""
    return pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', None, '2024-01-03']),
        'city_id': ['GB_LON', 'GB_LON', None],
        'avg_temp': [5.0, 6.0, 7.0]
    })

@pytest.fixture
def duplicate_key_dataframe():
    """DataFrame с дубликатами бизнес-ключа"""
    return pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-02']),
        'city_id': ['GB_LON', 'GB_LON', 'GB_LON'],
        'avg_temp': [5.0, 5.5, 6.0]
    })

@pytest.fixture
def temperature_out_of_range_dataframe():
    """DataFrame с температурой вне диапазона"""
    return pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'city_id': ['GB_LON', 'GB_LON'],
        'avg_temp': [100.0, -90.0],
        'min_temp': [95.0, -95.0],
        'max_temp': [105.0, -85.0],
        'total_precip': [0.0, 0.0]
    })

@pytest.fixture
def negative_precip_dataframe():
    """DataFrame с отрицательными осадками"""
    return pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'city_id': ['GB_LON', 'GB_LON'],
        'avg_temp': [5.0, 6.0],
        'total_precip': [-1.0, -0.5]
    })

@pytest.fixture
def humidity_out_of_range_dataframe():
    """DataFrame с влажностью вне [0,100]"""
    return pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'city_id': ['GB_LON', 'GB_LON'],
        'avg_humidity': [120, -10],
        'avg_temp': [5.0, 6.0]
    })

@pytest.fixture
def temp_logic_violation_dataframe():
    """DataFrame с нарушением min <= avg <= max"""
    return pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'city_id': ['GB_LON', 'GB_LON'],
        'min_temp': [10.0, 1.0],   # 10 > 8 (avg) - нарушение
        'avg_temp': [8.0, 5.0],
        'max_temp': [12.0, 4.0]    # 4 < 5 - нарушение
    })

# ========== Тесты ==========

class TestCheckTableNotEmpty:
    def test_pass_on_non_empty(self, good_dataframe):
        name, status, msg = check_table_not_empty(good_dataframe)
        assert status == "PASS"

    def test_fail_on_empty(self, empty_dataframe):
        name, status, msg = check_table_not_empty(empty_dataframe)
        assert status == "FAIL"

class TestCheckNoNullInKey:
    def test_pass_on_no_nulls(self, good_dataframe):
        name, status, msg = check_no_null_in_key(good_dataframe)
        assert status == "PASS"

    def test_fail_on_nulls(self, null_in_key_dataframe):
        name, status, msg = check_no_null_in_key(null_in_key_dataframe)
        assert status == "FAIL"
        assert "NULL" in msg

class TestCheckUniqueBusinessKey:
    def test_pass_on_unique(self, good_dataframe):
        name, status, msg = check_unique_business_key(good_dataframe)
        assert status == "PASS"

    def test_fail_on_duplicates(self, duplicate_key_dataframe):
        name, status, msg = check_unique_business_key(duplicate_key_dataframe)
        assert status == "FAIL"
        assert "дубликатов" in msg

class TestCheckTemperatureRange:
    def test_pass_on_normal_temps(self, good_dataframe):
        name, status, msg = check_temperature_range(good_dataframe)
        assert status == "PASS"

    def test_fail_on_out_of_range(self, temperature_out_of_range_dataframe):
        name, status, msg = check_temperature_range(temperature_out_of_range_dataframe)
        assert status == "FAIL"

class TestCheckNonNegativePrecipitation:
    def test_pass_on_non_negative(self, good_dataframe):
        name, status, msg = check_non_negative_precipitation(good_dataframe)
        assert status == "PASS"

    def test_warning_on_negative(self, negative_precip_dataframe):
        name, status, msg = check_non_negative_precipitation(negative_precip_dataframe)
        assert status == "WARNING"

class TestCheckHumidityRange:
    def test_pass_on_normal_humidity(self, good_dataframe):
        name, status, msg = check_humidity_range(good_dataframe)
        assert status == "PASS"

    def test_warning_on_out_of_range(self, humidity_out_of_range_dataframe):
        name, status, msg = check_humidity_range(humidity_out_of_range_dataframe)
        assert status == "WARNING"

class TestCheckTempMinMaxLogic:
    def test_pass_on_correct_logic(self, good_dataframe):
        name, status, msg = check_temp_min_max_logic(good_dataframe)
        assert status == "PASS"

    def test_fail_on_violation(self, temp_logic_violation_dataframe):
        name, status, msg = check_temp_min_max_logic(temp_logic_violation_dataframe)
        assert status == "FAIL"

# ========== Запуск тестов ==========
if __name__ == "__main__":
    pytest.main([__file__, "-v"])