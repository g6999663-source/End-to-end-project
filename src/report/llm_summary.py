import pandas as pd
import os
import requests
from pathlib import Path
import glob

def generate_summary():
    # 1. Поиск самого свежего файла
    base_dir = Path(__file__).resolve().parent.parent.parent
    list_of_files = glob.glob(str(base_dir / "data" / "mart" / "variant_04" / "*.csv"))
    
    if not list_of_files:
        print("Ошибка: CSV файлы не найдены.")
        return

    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    
    # 2. Формируем данные для нейросети
    stats_text = (f"Данные за {len(df)} дней. "
                  f"Средняя температура: {df['avg_temp_c'].mean():.1f}°C, "
                  f"максимум: {df['max_temp_c'].max():.1f}°C.")
    
    prompt = f"Проанализируй погоду в Лондоне: {stats_text}. Напиши краткий аналитический вывод на русском языке."
    
    # 3. Отправляем запрос в Ollama
    print("Генерирую отчет через Ollama (llama3.1)...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        summary = response.json()['response']
        
        # 4. Записываем РЕАЛЬНЫЙ ответ от нейросети в файл
        output_dir = base_dir / "docs" / "ml"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "llm_summary.md", "w", encoding="utf-8") as f:
            f.write("# Аналитический отчет по погоде\n\n")
            f.write(summary)
            
        print("Успех! Файл llm_summary.md обновлен текстом от нейросети.")
        
    except Exception as e:
        print(f"Ошибка при обращении к Ollama: {e}")

if __name__ == "__main__":
    generate_summary()
