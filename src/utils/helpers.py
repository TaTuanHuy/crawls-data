# src/utils/helpers.py
import os
import json
import time
import pandas as pd
from src.config.settings import OUTPUT_DIR

def save_to_json(data, filename):
    """Lưu dữ liệu vào file JSON"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filepath

def save_to_csv(data, filename):
    """Lưu dữ liệu vào file CSV"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding='utf-8')
    return filepath

def retry_on_failure(func, max_retries=3, delay=1):
    """Thử lại hàm khi gặp lỗi"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
    return wrapper