import pandas as pd
import json
import os

def run_data_quality_checks(period_start, period_end, **kwargs):
    """
    Проверяет качество данных. При FAIL задача падает.
    """
    start = period_start.split('T')[0]
    end = period_end.split('T')[0]
    
    mart_file = f"data/mart/variant_04/mart_{start}_{end}.csv"
    df = pd.read_csv(mart_file)
    
    checks = {
        'no_nulls_date': df['date'].notna().all(),
        'no_nulls_temp': df['avg_temp'].notna().all(),
        'min_le_avg_le_max': ((df['min_temp'] <= df['avg_temp']) & (df['avg_temp'] <= df['max_temp'])).all(),
        'temp_range': df['avg_temp'].between(-20, 45).all(),
        'unique_date': df['date'].is_unique
    }
    
    report = {
        'period': f"{start} → {end}",
        'total_rows': len(df),
        'checks': checks,
        'pass_count': sum(checks.values()),
        'fail_count': len(checks) - sum(checks.values())
    }
    
    os.makedirs('data', exist_ok=True)
    with open(f'data/dq_report_{start}_{end}.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"DQ report: {report['pass_count']} passed, {report['fail_count']} failed")
    
    # quality gate: если есть FAIL, поднимаем исключение
    if report['fail_count'] > 0:
        raise ValueError(f"DQ failed: {report['fail_count']} checks failed. Stop pipeline.")
    
    return report
