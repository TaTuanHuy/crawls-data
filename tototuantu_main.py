# tototuantu_main.py
import argparse
import sys
import os

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.crawlers.tototuantu_crawler import TotoTuanTuCrawler
from src.utils.logger import setup_logger

def main():
    # Thiết lập logger
    logger = setup_logger("tototuantu_main")
    
    # Tạo parser cho command line arguments
    parser = argparse.ArgumentParser(description='TotoTuanTu Crawler')
    parser.add_argument('--category', type=str, required=True, help='Category to crawl (e.g., bon-cau, lavabo)')
    parser.add_argument('--start_page', type=int, default=1, help='Start page number')
    parser.add_argument('--end_page', type=int, default=None, help='End page number')
    parser.add_argument('--filter', type=str, default=None, help='Filter parameter')
    parser.add_argument('--output', type=str, default='tototuantu_products', help='Output file prefix')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Khởi tạo crawler
    crawler = TotoTuanTuCrawler()
    
    try:
        # Crawl sản phẩm
        logger.info(f"Bắt đầu crawl danh mục: {args.category}")
        products = crawler.crawl_tototuantu_category(
            category=args.category,
            start_page=args.start_page,
            end_page=args.end_page,
            filter_param=args.filter
        )
        
        # Lưu dữ liệu
        if products:
            json_path, csv_path = crawler.save_products(products, prefix=args.output)
            logger.info(f"Đã lưu dữ liệu vào {json_path} và {csv_path}")
        else:
            logger.warning("Không tìm thấy sản phẩm nào")
        
    except Exception as e:
        logger.error(f"Lỗi không mong đợi: {str(e)}")
    
    finally:
        # Đóng trình duyệt
        crawler.close()

if __name__ == "__main__":
    main()