import os
import json
import csv
import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.crawlers.base_crawler import BaseCrawler
from src.config.settings import OUTPUT_DIR

class TotoCatalogCrawler(BaseCrawler):
    """Crawler chuyên biệt để thu thập dữ liệu chi tiết từ danh sách sản phẩm TOTO"""
    
    def __init__(self, input_json_path):
        """Khởi tạo crawler với tên cụ thể và đường dẫn đến file JSON đầu vào"""
        super().__init__(name="toto_catalog_crawler")
        self.input_json_path = input_json_path
        self.base_url = "https://tototuantu.vn"
        self.output_dir = os.path.join("src/test", "toto_products")
        
        # Thiết lập selectors cho tototuantu.vn (sử dụng từ TotoTuanTuCrawler)
        self.selectors = {
            'product_item': 'title-product',
            # 'name': 'h1.product-title',
            # 'price': '.product-price',
            # 'original_price': '.product-compare-price',
            # 'image': '.product-gallery img',
            # 'description': '.product-description',
            # 'specifications': '.product-specifications tr',
            # 'sku': '.product-sku',
            # 'product_gallery': '.product-gallery',
            # 'product_tabs': '.product-tabs',
            # 'product_promotion': '.product-promotion',
            # 'product_inventory': '.product-inventory span',
            # 'product_vendor': '.product-vendor a',
            # 'breadcrumb': '.breadcrumb-item a'
        }
        
        # Tạo thư mục đầu ra nếu chưa tồn tại
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Đọc dữ liệu từ file JSON đầu vào
        self.products = self.load_input_json()
        
    def load_input_json(self):
        """Đọc dữ liệu từ file JSON đầu vào"""
        try:
            with open(self.input_json_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            self.logger.info(f"Đã đọc {len(products)} sản phẩm từ file JSON đầu vào")
            return products
        except Exception as e:
            self.logger.error(f"Lỗi khi đọc file JSON đầu vào: {str(e)}")
            return []
    
    def check_page_exists(self):
        """Kiểm tra xem trang sản phẩm có tồn tại hay trả về lỗi 404"""
        try:
            # Tìm các chỉ báo lỗi 404
            error_elements = self.find_elements("//div[contains(text(), 'TRANG KHÔNG ĐƯỢC TÌM THẤY')]", By.XPATH)
            if error_elements:
                self.logger.error("Lỗi 404: Không tìm thấy trang sản phẩm")
                return False
                
            # Kiểm tra sự hiện diện của nội dung sản phẩm để xác nhận trang tồn tại
            product_element = self.find_element(".product-detail", wait_time=5)
            return product_element is not None
        except TimeoutException:
            self.logger.error("Hết thời gian chờ trang sản phẩm tải")
            return False
    
    def get_text_from_element(self, parent_element, selector):
        """
        Lấy text từ phần tử con của parent_element (từ TotoTuanTuCrawler)
        
        Args:
            parent_element: Phần tử cha
            selector (str): CSS selector của phần tử con
            
        Returns:
            str: Text của phần tử con
        """
        try:
            element = parent_element.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return None
    
    def extract_product_details(self, product_url, base_product_data):
        """Thu thập thông tin chi tiết của sản phẩm từ URL (sử dụng phương pháp từ TotoTuanTuCrawler)"""
        self.logger.info(f"Đang thu thập dữ liệu chi tiết cho sản phẩm: {product_url}")
        
        # Khởi tạo dữ liệu sản phẩm với dữ liệu cơ bản từ JSON đầu vào
        product_data = {
            **base_product_data,
            'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'product_exists': False
        }
        
        try:
            # Điều hướng đến trang sản phẩm
            self.navigate_to(product_url)
            
            # Kiểm tra xem trang sản phẩm có tồn tại không
            if "TRANG KHÔNG ĐƯỢC TÌM THẤY" in self.driver.page_source:
                self.logger.warning(f"Trang sản phẩm không tồn tại: {product_url}")
                return product_data
            
            # Sản phẩm tồn tại, cập nhật trạng thái
            # product_data["product_exists"] = True
            
            # Thu thập tên sản phẩm (nếu không có trong dữ liệu gốc)
            if not product_data.get('title-product'):
                product_data['title-product'] = self.get_text('.title-product')
            
            # Thu thập giá sản phẩm (nếu không có trong dữ liệu gốc)
            # if not product_data.get('price'):
            #     product_data['price'] = self.get_text(self.selectors['price'])
            
            # Thu thập giá gốc (nếu không có trong dữ liệu gốc)
            # if not product_data.get('original_price'):
            #     product_data['original_price'] = self.get_text(self.selectors['original_price'])
            
            # Thu thập mã sản phẩm (SKU)
            # if not product_data.get("sku") or product_data.get("sku") is None:
            #     sku_text = self.get_text(self.selectors['sku'])
            #     if sku_text:
            #         # Xử lý chuỗi SKU, loại bỏ "SKU:" nếu có
            #         sku = sku_text.replace("SKU:", "").strip()
            #         product_data["sku"] = sku
            #         self.logger.info(f"Mã sản phẩm: {sku}")
            #     else:
            #         # Thử trích xuất mã từ tên sản phẩm
            #         name = product_data.get('name', '')
            #         sku_match = re.search(r'[A-Z0-9]+-[A-Z0-9]+', name)
            #         product_data['sku'] = sku_match.group(0) if sku_match else None
            
            # Thu thập mô tả sản phẩm
            # description = self.get_text(self.selectors['description'])
            # if description:
            #     product_data["description"] = description
            #     self.logger.info("Đã thu thập mô tả sản phẩm")
            
            # Thu thập thông số kỹ thuật
            # specs = self.extract_specifications()
            # if specs:
            #     product_data["specifications"] = specs
            #     self.logger.info(f"Đã thu thập {len(specs)} thông số kỹ thuật")
            
            # Thu thập hình ảnh sản phẩm
            # images = self.extract_product_images()
            # if images:
                # Đảm bảo image_url chính đã có trong danh sách
                # if product_data.get("image_url") and product_data["image_url"] not in images:
                #     images.insert(0, product_data["image_url"])
                # product_data["all_images"] = images
                # self.logger.info(f"Đã thu thập {len(images)} hình ảnh sản phẩm")
            
            # # Thu thập thông tin thêm (nếu có)
            # additional_info = self.extract_additional_info()
            # if additional_info:
            #     product_data["additional_info"] = additional_info
            #     self.logger.info("Đã thu thập thông tin bổ sung")
            
            # # Thu thập thông tin khuyến mãi
            # promotion = self.get_text(self.selectors['product_promotion'])
            # if promotion:
            #     product_data["promotion"] = promotion
            #     self.logger.info("Đã thu thập thông tin khuyến mãi")
            
            # # Thu thập thông tin tình trạng hàng
            # stock_status = self.get_text(self.selectors['product_inventory'])
            # if stock_status:
            #     product_data["stock_status"] = stock_status
            #     self.logger.info(f"Tình trạng hàng: {stock_status}")
            
            # # Thu thập thông tin thương hiệu
            # brand = self.get_text(self.selectors['product_vendor'])
            # if brand:
            #     product_data["brand"] = brand
            #     self.logger.info(f"Thương hiệu: {brand}")
            
            # # Thu thập thông tin danh mục
            # breadcrumbs = self.find_elements(self.selectors['breadcrumb'])
            # if breadcrumbs and len(breadcrumbs) > 1:
            #     categories = []
            #     for breadcrumb in breadcrumbs[1:]:  # Bỏ qua "Trang chủ"
            #         categories.append(breadcrumb.text.strip())
            #     if categories:
            #         product_data["categories"] = categories
            #         self.logger.info(f"Danh mục: {', '.join(categories)}")
            return product_data
            
        except Exception as e:
            self.logger.error(f"Lỗi khi thu thập dữ liệu sản phẩm: {str(e)}")
            return product_data
    
    def extract_specifications(self):
        """Trích xuất thông số kỹ thuật sản phẩm (sử dụng phương pháp từ TotoTuanTuCrawler)"""
        specs = {}
        try:
            # Tìm bảng thông số kỹ thuật
            spec_rows = self.find_elements(self.selectors['specifications'])
            
            # Trích xuất dữ liệu từ các hàng
            for row in spec_rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        if key:  # Chỉ thêm nếu key không trống
                            specs[key] = value
                except Exception as e:
                    self.logger.warning(f"Lỗi khi xử lý hàng thông số: {str(e)}")
            
            return specs
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất thông số kỹ thuật: {str(e)}")
            return {}
    
    def extract_product_images(self):
        """Trích xuất hình ảnh sản phẩm (sử dụng phương pháp từ TotoTuanTuCrawler)"""
        images = []
        try:
            # Tìm tất cả các phần tử hình ảnh trong gallery
            image_elements = self.find_elements(self.selectors['image'])
            
            # Trích xuất URL hình ảnh
            for img in image_elements:
                try:
                    # Ưu tiên thuộc tính data-src (lazy loading) hoặc src
                    img_url = img.get_attribute("src")
                    if not img_url or img_url.endswith("blank.png"):
                        img_url = img.get_attribute("data-src")
                    
                    if img_url and not img_url.endswith('.svg') and "medium" not in img_url:  # Bỏ qua các icon SVG và ảnh thumbnail
                        # Đảm bảo URL đầy đủ
                        if img_url.startswith('/'):
                            img_url = f"{self.base_url}{img_url}"
                        if img_url not in images:  # Tránh trùng lặp
                            images.append(img_url)
                except Exception as e:
                    self.logger.warning(f"Lỗi khi xử lý hình ảnh: {str(e)}")
            
            return images
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất hình ảnh sản phẩm: {str(e)}")
            return []
    
    def extract_additional_info(self):
        """Trích xuất thông tin bổ sung như tính năng, ưu đãi, v.v."""
        additional_info = {}
        try:
            # Tìm các tab thông tin bổ sung
            tabs = self.find_elements(f"{self.selectors['product_tabs']} a")
            
            for tab in tabs:
                try:
                    tab_name = tab.text.strip()
                    if tab_name and tab_name.lower() not in ['mô tả', 'thông số kỹ thuật']:
                        # Click vào tab để hiển thị nội dung
                        tab.click()
                        time.sleep(1)
                        
                        # Lấy nội dung tab
                        tab_content = self.get_text("//div[contains(@class, 'tab-content') and contains(@class, 'active')]", By.XPATH)
                        if tab_content:
                            additional_info[tab_name] = tab_content
                except Exception as e:
                    self.logger.warning(f"Lỗi khi xử lý tab {tab.text}: {str(e)}")
            
            return additional_info
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất thông tin bổ sung: {str(e)}")
            return {}
    
    def process_all_products(self, limit=None):
        """Xử lý tất cả sản phẩm từ danh sách đầu vào"""
        results = []
        total_products = len(self.products)
        processed_count = 0
        
        self.logger.info(f"Bắt đầu xử lý {total_products} sản phẩm")
        
        for i, product in enumerate(self.products):
            if limit and i >= limit:
                self.logger.info(f"Đã đạt đến giới hạn {limit} sản phẩm")
                break
                
            self.logger.info(f"Đang xử lý sản phẩm {i+1}/{total_products}: {product.get('name', 'Không có tên')}")
            
            try:
                # Thu thập thông tin chi tiết
                product_url = product.get('product_url')
                if not product_url:
                    self.logger.warning(f"Sản phẩm {i+1} không có URL, bỏ qua")
                    continue
                    
                detailed_product = self.extract_product_details(product_url, product)
                results.append(detailed_product)
                processed_count += 1
                
                # Lưu kết quả trung gian sau mỗi 5 sản phẩm
                if processed_count % 5 == 0:
                    self.save_results(results)
                    self.logger.info(f"Đã lưu kết quả trung gian sau khi xử lý {processed_count}/{total_products} sản phẩm")
                
                # Tạm dừng giữa các yêu cầu để tránh quá tải máy chủ
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Lỗi khi xử lý sản phẩm {i+1}: {str(e)}")
        
        # Lưu kết quả cuối cùng
        if results:
            self.save_results(results)
            self.logger.info(f"Đã hoàn thành xử lý {processed_count}/{total_products} sản phẩm")
        
        return results
    
    def save_results(self, results):
        """Lưu kết quả vào file JSON và CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Lưu file JSON
        json_filename = os.path.join(self.output_dir, f"toto_products_detailed_{timestamp}.json")
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Đã lưu kết quả vào file JSON: {json_filename}")
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu file JSON: {str(e)}")
        
        # Lưu file CSV
        csv_filename = os.path.join(self.output_dir, f"toto_products_detailed_{timestamp}.csv")
        try:
            # Xác định tất cả các trường có thể có
            fieldnames = set()
            for product in results:
                for key in product.keys():
                    if key != 'specifications' and key != 'additional_info' and key != 'all_images':
                        fieldnames.add(key)
            
            fieldnames = sorted(list(fieldnames))
            
            with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in results:
                    # Tạo bản sao của sản phẩm chỉ với các trường cơ bản
                    product_copy = {}
                    for key in fieldnames:
                        if key in product:
                            # Xử lý các trường đặc biệt
                            if isinstance(product[key], list):
                                product_copy[key] = ', '.join(str(item) for item in product[key])
                            elif isinstance(product[key], dict):
                                product_copy[key] = json.dumps(product[key], ensure_ascii=False)
                            else:
                                product_copy[key] = product[key]
                        else:
                            product_copy[key] = ''
                    
                    writer.writerow(product_copy)
            
            self.logger.info(f"Đã lưu kết quả vào file CSV: {csv_filename}")
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu file CSV: {str(e)}")
        
        return json_filename, csv_filename

def main():
    """Hàm chính để chạy crawler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TOTO Catalog Crawler')
    parser.add_argument('--input', type=str, required=True, help='Đường dẫn đến file JSON đầu vào')
    parser.add_argument('--limit', type=int, default=None, help='Giới hạn số lượng sản phẩm cần xử lý')
    
    args = parser.parse_args()
    
    # Khởi tạo crawler
    crawler = TotoCatalogCrawler(args.input)
    
    try:
        # Xử lý tất cả sản phẩm
        crawler.process_all_products(limit=args.limit)
    except Exception as e:
        crawler.logger.error(f"Lỗi trong quá trình xử lý: {str(e)}")
    finally:
        # Đóng trình duyệt
        crawler.close()

if __name__ == "__main__":
    main()