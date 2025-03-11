# src/utils/logger.py
import logging
from src.config.settings import LOG_FILE

def setup_logger(name):
    """Thiết lập logger với tên được chỉ định"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Tạo file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    
    # Tạo console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Tạo formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Thêm handlers vào logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger