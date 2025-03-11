# main.py
import argparse
import sys
import os

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.crawlers.product_crawler import ProductCrawler
from src.utils.logger import setup_logger

def main():
    # Thiết lập logger
    logger = setup_logger("main")
    
    # Tạo parser cho command line arguments
    parser = argparse.ArgumentParser(description='Product Crawler')
    parser.add_argument('--url', type=str, required=True, help='URL to crawl')
    parser.add_argument('--pages', type=int, default=None, help='Maximum number of pages to crawl')
    parser.add_argument('--output', type=str, default='products', help='Output file prefix')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Thiết lập selectors cho trang web cụ thể
    # Thay đổi các selector này để phù hợp với trang web bạn muốn crawl
    selectors = {
        'product_item': '.product-item',  # Selector cho container sản phẩm
        'name': '.product-name',          # Selector cho tên sản phẩm
        'price': '.product-price',        # Selector cho giá sản phẩm
        'image_attr_src': '.product-image img',  # Selector cho hình ảnh + thuộc tính src
        'description': '.product-description',  # Selector cho mô tả
        'category': '.product-category',  # Selector cho danh mục
        'rating': '.product-rating',      # Selector cho đánh giá
        'next_page': '.pagination .next'  # Selector cho nút "Trang tiếp theo"
    }
    
    # Khởi tạo crawler
    crawler = ProductCrawler()
    
    try:
        # Crawl sản phẩm
        logger.info(f"Bắt đầu crawl từ URL: {args.url}")
        products = crawler.crawl_products(args.url, selectors, max_pages=args.pages)
        
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