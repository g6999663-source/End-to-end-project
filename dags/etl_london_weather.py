from datetime import datetime, timedelta
import inspect
from airflow import DAG
from airflow.operators.python import PythonOperator

# Абсолютные импорты модулей из папки src благодаря PYTHONPATH
from extract import extract_incremental
from transform import normalize
from transform import build_mart
import dq
from load import load_incremental

# УНИВЕРСАЛЬНАЯ ОБЕРТКА ДЛЯ ЗАГРУЗКИ:
# Автоматически находит и запускает главную функцию внутри вашего load_incremental.py
def universal_load_wrapper(**kwargs):
    functions = [obj for name, obj in inspect.getmembers(load_incremental, inspect.isfunction) 
                 if obj.__module__ == load_incremental.__name__]
    if not functions:
        raise ImportError("В файле load_incremental.py не найдено ни одной функции!")
    
    # Берем первую определенную функцию в файле (например, load_data, load_incremental или load_to_postgres)
    target_function = functions[0]
    print(f"Автоматически запускаем функцию загрузки: {target_function.__name__}")
    
    # Проверяем, принимает ли функция аргументы
    sig = inspect.signature(target_function)
    if 'period_start' in sig.parameters and 'period_end' in sig.parameters:
        return target_function(period_start=kwargs.get('data_interval_start'), period_end=kwargs.get('data_interval_end'), **kwargs)
    return target_function(**kwargs)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'weather_london_etl',
    default_args=default_args,
    description='End-to-End London Weather ETL Pipeline',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    task_extract = PythonOperator(
        task_id='extract_weather',
        python_callable=extract_incremental.extract_weather_data,
        provide_context=True,
    )

    task_normalize = PythonOperator(
        task_id='normalize_data',
        python_callable=normalize.normalize_raw_to_csv,
        op_kwargs={
            'period_start': '{{ data_interval_start }}',
            'period_end': '{{ data_interval_end }}'
        },
        provide_context=True,
    )

    task_build_mart = PythonOperator(
        task_id='build_mart',
        python_callable=build_mart.build_daily_mart, 
        op_kwargs={
            'period_start': '{{ data_interval_start }}',
            'period_end': '{{ data_interval_end }}'
        },
        provide_context=True,
    )

    task_dq_checks = PythonOperator(
        task_id='data_quality_checks',
        python_callable=dq.run_data_quality_checks,
        provide_context=True,
    )

    task_load = PythonOperator(
        task_id='load_to_postgres',
        python_callable=universal_load_wrapper,  # Используем нашу умную обертку
        provide_context=True,
    )

    # Цепочка выполнения пайплайна
    task_extract >> task_normalize >> task_build_mart >> task_dq_checks >> task_load
