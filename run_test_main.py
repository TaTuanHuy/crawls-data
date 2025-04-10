import os
import sys
import argparse
from src.crawlers.test import TotoCatalogCrawler

def main():
    """Hàm chính để chạy crawler từ dòng lệnh"""
    
    # Sử dụng argparse để xử lý tham số dòng lệnh
    parser = argparse.ArgumentParser(description='TOTO Catalog Crawler')
    parser.add_argument('--input', '-i', type=str, required=True, help='Đường dẫn đến file JSON đầu vào')
    parser.add_argument('--output', '-o', type=str, default=None, help='Thư mục đầu ra cho kết quả')
    parser.add_argument('--limit', '-l', type=int, default=None, help='Giới hạn số lượng sản phẩm cần xử lý')
    
    args = parser.parse_args()
    
    # Kiểm tra file đầu vào tồn tại
    if not os.path.exists(args.input):
        print(f"Lỗi: File {args.input} không tồn tại")
        sys.exit(1)
    
    # Khởi tạo crawler với thư mục đầu ra tùy chỉnh nếu được cung cấp
    crawler = TotoCatalogCrawler(args.input, output_dir=args.output)
    
    try:
        # Xử lý tất cả sản phẩm
        print(f"Bắt đầu xử lý sản phẩm từ file {args.input}")
        if args.limit:
            print(f"Giới hạn xử lý: {args.limit} sản phẩm")
        if args.output:
            print(f"Thư mục đầu ra: {args.output}")
        
        crawler.process_all_products(limit=args.limit)
        print("Hoàn thành xử lý sản phẩm")
        
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý: {str(e)}")
    finally:
        # Đóng trình duyệt
        crawler.close()

if __name__ == "__main__":
    main()