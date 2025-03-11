# src/config/settings.py
import os
from datetime import datetime

# Thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thư mục output
OUTPUT_DIR = os.path.join(BASE_DIR, 'src', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Thư mục logs
LOGS_DIR = os.path.join(BASE_DIR, 'src', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Tên file log
LOG_FILE = os.path.join(LOGS_DIR, f'crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Cấu hình Selenium
SELENIUM_CONFIG = {
    'browser': 'firefox',  # 'firefox' hoặc 'chrome'
    'headless': False,     # True để chạy ẩn, False để hiển thị UI
    'implicit_wait': 10,   # Thời gian chờ mặc định (giây)
    'page_load_timeout': 30,  # Thời gian chờ tải trang (giây)
}

# User-Agent
USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'

# Thời gian delay giữa các request (giây)
REQUEST_DELAY = 2

# Số lần thử lại khi request thất bại
MAX_RETRIES = 3