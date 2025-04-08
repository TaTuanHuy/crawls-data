import os
import sys
from src.crawlers.test import TotoCatalogCrawler

def main():
    """Hàm chính để chạy crawler từ dòng lệnh"""
    
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python run_catalog_crawler.py <đường_dẫn_file_json> [số_lượng_giới_hạn]")
        sys.exit(1)
    
    # Lấy đường dẫn file JSON đầu vào
    input_json_path = sys.argv[1]
    
    # Kiểm tra file tồn tại
    if not os.path.exists(input_json_path):
        print(f"Lỗi: File {input_json_path} không tồn tại")
        sys.exit(1)
    
    # Lấy giới hạn số lượng sản phẩm (nếu có)
    limit = None
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            print("Lỗi: Giới hạn phải là một số nguyên")
            sys.exit(1)
    
    # Khởi tạo crawler
    crawler = TotoCatalogCrawler(input_json_path)
    
    try:
        # Xử lý tất cả sản phẩm
        print(f"Bắt đầu xử lý sản phẩm từ file {input_json_path}")
        if limit:
            print(f"Giới hạn xử lý: {limit} sản phẩm")
        
        crawler.process_all_products(limit=limit)
        print("Hoàn thành xử lý sản phẩm")
        
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý: {str(e)}")
    finally:
        # Đóng trình duyệt
        crawler.close()

if __name__ == "__main__":
    main()