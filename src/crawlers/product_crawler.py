# src/crawlers/product_crawler.py
import time
import json
from src.crawlers.base_crawler import BaseCrawler
from src.utils.helpers import save_to_json, save_to_csv
from selenium.webdriver.common.by import By

class ProductCrawler(BaseCrawler):
    """Crawler chuyên dụng cho việc crawl sản phẩm"""
    
    def __init__(self):
        """Khởi tạo ProductCrawler"""
        super().__init__(name="product_crawler")
    
    def crawl_products(self, url, selectors, max_pages=None):
        """
        Crawl dữ liệu sản phẩm từ trang web
        
        Args:
            url (str): URL của trang web cần crawl
            selectors (dict): Dictionary chứa các CSS selector cho từng thông tin
                Ví dụ: {
                    'product_item': '.product-item',
                    'name': '.product-name',
                    'price': '.product-price',
                    'image': 'img.product-image',
                    'description': '.product-description',
                    'next_page': '.pagination .next'
                }
            max_pages (int, optional): Số trang tối đa cần crawl. Mặc định là None (crawl tất cả).
        
        Returns:
            list: Danh sách các sản phẩm đã crawl
        """
        # Danh sách lưu sản phẩm
        products = []
        
        try:
            # Truy cập trang web
            self.navigate_to(url)
            
            # Xử lý phân trang
            for page in self.handle_pagination(selectors.get('next_page'), max_pages):
                self.logger.info(f"Đang xử lý trang {page}")
                
                # Tìm tất cả sản phẩm trên trang
                product_items = self.find_elements(selectors.get('product_item'))
                self.logger.info(f"Đã tìm thấy {len(product_items)} sản phẩm trên trang {page}")
                
                # Trích xuất thông tin từ mỗi sản phẩm
                for index, item in enumerate(product_items):
                    try:
                        product = {}
                        
                        # Trích xuất từng thông tin theo selector
                        for key, selector in selectors.items():
                            # Bỏ qua các selector đặc biệt
                            if key in ['product_item', 'next_page']:
                                continue
                                
                            # Xử lý các trường hợp đặc biệt
                            if key.endswith('_attr'):
                                # Trích xuất thuộc tính (ví dụ: src của hình ảnh)
                                attr_name = key.split('_attr_')[1] if '_attr_' in key else 'src'
                                base_selector = selector
                                try:
                                    element = item.find_element(By.CSS_SELECTOR, base_selector)
                                    product[key.split('_attr')[0]] = element.get_attribute(attr_name)
                                except:
                                    product[key.split('_attr')[0]] = None
                            else:
                                # Trích xuất text
                                try:
                                    element = item.find_element(By.CSS_SELECTOR, selector)
                                    product[key] = element.text.strip()
                                except:
                                    product[key] = None
                        
                        # Thêm vào danh sách
                        products.append(product)
                        self.logger.debug(f"Đã xử lý sản phẩm {index + 1}/{len(product_items)} trên trang {page}")
                        
                    except Exception as e:
                        self.logger.error(f"Lỗi khi xử lý sản phẩm {index + 1} trên trang {page}: {str(e)}")
            
            self.logger.info(f"Đã crawl tổng cộng {len(products)} sản phẩm")
            return products
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl sản phẩm: {str(e)}")
            return products
    
    def crawl_product_details(self, product_urls, selectors):
        """
        Crawl thông tin chi tiết của các sản phẩm
        
        Args:
            product_urls (list): Danh sách URL của các sản phẩm cần crawl
            selectors (dict): Dictionary chứa các CSS selector cho từng thông tin
                Ví dụ: {
                    'name': 'h1.product-title',
                    'price': '.product-price',
                    'description': '.product-description',
                    'specs': '.product-specs tr',
                    'spec_key': 'td:nth-child(1)',
                    'spec_value': 'td:nth-child(2)'
                }
        
        Returns:
            list: Danh sách thông tin chi tiết của các sản phẩm
        """
        # Danh sách lưu thông tin chi tiết sản phẩm
        product_details = []
        
        for index, url in enumerate(product_urls):
            try:
                self.logger.info(f"Đang xử lý sản phẩm {index + 1}/{len(product_urls)}: {url}")
                
                # Truy cập trang chi tiết sản phẩm
                self.navigate_to(url)
                
                # Trích xuất thông tin chi tiết
                product_detail = {'url': url}
                
                # Trích xuất các thông tin cơ bản
                for key, selector in selectors.items():
                    # Bỏ qua các selector đặc biệt
                    if key in ['specs', 'spec_key', 'spec_value']:
                        continue
                        
                    # Xử lý các trường hợp đặc biệt
                    if key.endswith('_attr'):
                        # Trích xuất thuộc tính
                        attr_name = key.split('_attr_')[1] if '_attr_' in key else 'src'
                        base_selector = selector
                        product_detail[key.split('_attr')[0]] = self.get_attribute(base_selector, attr_name)
                    else:
                        # Trích xuất text
                        product_detail[key] = self.get_text(selector)
                
                # Trích xuất thông số kỹ thuật (nếu có)
                if 'specs' in selectors and 'spec_key' in selectors and 'spec_value' in selectors:
                    specs = {}
                    spec_rows = self.find_elements(selectors['specs'])
                    
                    for row in spec_rows:
                        try:
                            key = row.find_element(By.CSS_SELECTOR, selectors['spec_key']).text.strip()
                            value = row.find_element(By.CSS_SELECTOR, selectors['spec_value']).text.strip()
                            if key:
                                specs[key] = value
                        except:
                            continue
                    
                    product_detail['specifications'] = specs
                
                # Thêm vào danh sách
                product_details.append(product_detail)
                self.logger.info(f"Đã xử lý xong sản phẩm: {product_detail.get('name', url)}")
                
            except Exception as e:
                self.logger.error(f"Lỗi khi xử lý URL {url}: {str(e)}")
                continue
        
        self.logger.info(f"Đã crawl chi tiết của {len(product_details)} sản phẩm")
        return product_details
    
    def save_products(self, products, prefix="products"):
        """Lưu danh sách sản phẩm vào file JSON và CSV"""
        if not products:
            self.logger.warning("Không có dữ liệu sản phẩm để lưu")
            return None, None
        
        # Tạo tên file với timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        json_filename = f"{prefix}_{timestamp}.json"
        csv_filename = f"{prefix}_{timestamp}.csv"
        
        # Lưu dữ liệu
        json_path = save_to_json(products, json_filename)
        csv_path = save_to_csv(products, csv_filename)
        
        self.logger.info(f"Đã lưu {len(products)} sản phẩm vào {json_path} và {csv_path}")
        
        return json_path, csv_path