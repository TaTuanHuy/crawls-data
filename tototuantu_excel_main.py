import argparse
import sys
import os

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from tototuantu_excel_crawler import TotoTuanTuExcelCrawler
from src.crawlers.tototuantu_excel_crawler import TotoTuanTuExcelCrawler
from src.utils.logger import setup_logger

def main():
    # Thiết lập logger
    logger = setup_logger("tototuantu_excel_main")
    
    # Tạo parser cho command line arguments
    parser = argparse.ArgumentParser(description='TotoTuanTu Excel Crawler')
    parser.add_argument('--category', type=str, required=True, help='Category to crawl (e.g., bon-cau, lavabo)')
    parser.add_argument('--start_page', type=int, default=1, help='Start page number')
    parser.add_argument('--end_page', type=int, default=None, help='End page number')
    parser.add_argument('--filter', type=str, default=None, help='Filter parameter')
    parser.add_argument('--no_details', action='store_true', help='Skip crawling product details')
    parser.add_argument('--output', type=str, default='tototuantu_products', help='Output file prefix')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Khởi tạo crawler
    crawler = TotoTuanTuExcelCrawler()
    
    try:
        # Crawl sản phẩm và lưu vào Excel
        products, excel_path = crawler.crawl_and_save_to_excel(
            category=args.category,
            start_page=args.start_page,
            end_page=args.end_page,
            filter_param=args.filter,
            crawl_details=not args.no_details,
            prefix=args.output
        )
        
        if excel_path:
            logger.info(f"Đã crawl và lưu {len(products)} sản phẩm vào {excel_path}")
        else:
            logger.warning("Không tìm thấy sản phẩm nào hoặc có lỗi khi lưu dữ liệu")
        
    except Exception as e:
        logger.error(f"Lỗi không mong đợi: {str(e)}")
    
    finally:
        # Đóng trình duyệt
        crawler.close()

if __name__ == "__main__":
    main()