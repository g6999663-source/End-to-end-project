import sys
import os
import argparse
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.extract.extract_incremental import extract_incremental
from src.transform.normalize import normalize_raw_to_csv
from src.transform.build_mart import build_daily_mart
from src.load.load_incremental import load_to_postgres

def run_pipeline(mode, config_path="configs/variant_04.yml"):
    print(f"Starting pipeline in {mode} mode...")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    city_id = config['entity']['city_id']

    # Extract
    raw_data = extract_incremental(config, mode=mode)
    if raw_data is None:
        print("No new data to process")
        return

    # Normalize
    normalized_df = normalize_raw_to_csv(raw_data, city_id=city_id)
    if normalized_df is None:
        print("Normalization failed")
        return

    # Build mart
    mart_df = build_daily_mart()
    if mart_df is None:
        print("Mart building failed")
        return

    # Load
    load_to_postgres("data/mart/variant_04/daily_weather.csv", "daily_weather", mode=mode)

    print(f"Pipeline completed successfully in {mode} mode!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    args = parser.parse_args()
    run_pipeline(args.mode)