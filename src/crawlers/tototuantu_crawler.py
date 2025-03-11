# src/crawlers/tototuantu_crawler.py
from src.crawlers.base_crawler import BaseCrawler
from src.crawlers.product_crawler import ProductCrawler
from selenium.webdriver.common.by import By
from urllib.parse import urlencode
import time
import re

class TotoTuanTuCrawler(ProductCrawler):
    """Crawler chuyên dụng cho tototuantu.vn"""
    
    def __init__(self):
        """Khởi tạo TotoTuanTuCrawler"""
        super().__init__()
        self.logger.info("Khởi tạo TotoTuanTuCrawler")
        self.base_url = "https://tototuantu.vn"
    
    def build_url(self, category, page=1, filter_param=None):
        """
        Xây dựng URL cho danh mục và trang cụ thể
        
        Args:
            category (str): Tên danh mục (ví dụ: 'bon-cau', 'lavabo')
            page (int): Số trang
            filter_param (str, optional): Tham số filter (nếu có)
            
        Returns:
            str: URL đầy đủ
        """
        url = f"{self.base_url}/collections/{category}"
        
        # Xây dựng query parameters
        params = {}
        if filter_param:
            params['q'] = filter_param
        params['page'] = page
        params['view'] = 'grid'
        
        # Thêm query parameters vào URL
        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
        return url
    
    def crawl_tototuantu_category(self, category, start_page=1, end_page=None, filter_param=None):
        """
        Crawl sản phẩm từ một danh mục trên tototuantu.vn
        
        Args:
            category (str): Tên danh mục (ví dụ: 'bon-cau', 'lavabo')
            start_page (int): Trang bắt đầu
            end_page (int, optional): Trang kết thúc. Nếu None, sẽ crawl đến trang cuối cùng.
            filter_param (str, optional): Tham số filter (nếu có)
            
        Returns:
            list: Danh sách sản phẩm
        """
        products = []
        current_page = start_page
        
        while True:
            # Xây dựng URL cho trang hiện tại
            url = self.build_url(category, current_page, filter_param)
            
            self.logger.info(f"Đang crawl trang: {url}")
            self.navigate_to(url)
            
            # Kiểm tra xem trang có tồn tại không
            if "TRANG KHÔNG ĐƯỢC TÌM THẤY" in self.driver.page_source:
                self.logger.warning("Trang không tồn tại!")
                break
            
            # Thiết lập selectors cho tototuantu.vn
            selectors = {
                'product_item': '.item_product_main',
                'name': '.product-name a',
                'price': '.price-box .price',
                'original_price': '.price-box .compare-price',
                'image_attr_src': '.product-thumbnail .product-thumbnail__img',
                'next_page': '.section pagenav .pagination li:last-child a'
            }
            
            # Tìm tất cả sản phẩm trên trang
            product_elements = self.find_elements(selectors['product_item'])
            self.logger.info(f"Đã tìm thấy {len(product_elements)} sản phẩm trên trang {current_page}")
            
            # Nếu không tìm thấy sản phẩm nào, có thể đã đến trang cuối
            if not product_elements:
                self.logger.info(f"Không tìm thấy sản phẩm nào trên trang {current_page}. Có thể đã đến trang cuối.")
                break
            
            # Trích xuất thông tin từ mỗi sản phẩm
            for index, product_element in enumerate(product_elements):
                try:
                    product = {}
                    
                    # Trích xuất tên sản phẩm
                    product['name'] = self.get_text_from_element(product_element, selectors['name'])
                    
                    # Trích xuất URL sản phẩm
                    product['product_url'] = product_element.find_element(By.CSS_SELECTOR, "a.image_thumb").get_attribute("href")
                    
                    # Trích xuất giá sản phẩm
                    product['price'] = self.get_text_from_element(product_element, selectors['price'])
                    
                    # Trích xuất giá gốc (nếu có)
                    try:
                        product['original_price'] = self.get_text_from_element(product_element, selectors['original_price'])
                    except:
                        product['original_price'] = None
                    
                    # Trích xuất hình ảnh sản phẩm
                    img_element = product_element.find_element(By.CSS_SELECTOR, selectors['image_attr_src'])
                    img_url = img_element.get_attribute("src")
                    
                    # Đôi khi src là lazy-loaded, nên cần kiểm tra data-src
                    if not img_url or img_url.endswith("blank.png"):
                        img_url = img_element.get_attribute("data-src")
                    
                    product['image_url'] = img_url
                    
                    # Trích xuất mã sản phẩm (nếu có)
                    try:
                        sku_element = product_element.find_element(By.CSS_SELECTOR, ".product-sku")
                        product['sku'] = sku_element.text.strip()
                    except:
                        # Thử trích xuất mã từ tên sản phẩm
                        sku_match = re.search(r'[A-Z0-9]+-[A-Z0-9]+', product['name'])
                        product['sku'] = sku_match.group(0) if sku_match else None
                    
                    # Thêm thông tin danh mục
                    product['category'] = category
                    
                    # Thêm vào danh sách
                    products.append(product)
                    self.logger.info(f"Đã xử lý sản phẩm {index + 1}/{len(product_elements)}: {product['name']}")
                    
                except Exception as e:
                    self.logger.error(f"Lỗi khi xử lý sản phẩm {index + 1}: {str(e)}")
            
            # Kiểm tra xem đã đến trang cuối chưa
            if end_page and current_page >= end_page:
                self.logger.info(f"Đã đạt đến trang cuối cùng: {end_page}")
                break
            
            # Chuyển đến trang tiếp theo
            current_page += 1
        
        self.logger.info(f"Đã crawl tổng cộng {len(products)} sản phẩm từ danh mục {category}")
        return products
    
    def get_text_from_element(self, parent_element, selector):
        """
        Lấy text từ phần tử con của parent_element
        
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
    
    def crawl_tototuantu_product_detail(self, product_url):
        """
        Crawl thông tin chi tiết của sản phẩm trên tototuantu.vn
        
        Args:
            product_url (str): URL của sản phẩm
            
        Returns:
            dict: Thông tin chi tiết của sản phẩm
        """
        self.logger.info(f"Đang crawl chi tiết sản phẩm: {product_url}")
        self.navigate_to(product_url)
        
        try:
            # Trích xuất thông tin cơ bản
            product_detail = {
                'url': product_url,
                'name': self.get_text("h1.product-title"),
                'price': self.get_text(".product-price"),
                'original_price': self.get_text(".product-compare-price"),
            }
            
            # Trích xuất hình ảnh sản phẩm
            images = []
            img_elements = self.find_elements(".product-gallery img")
            for img in img_elements:
                img_url = img.get_attribute("src")
                if not img_url or img_url.endswith("blank.png"):
                    img_url = img.get_attribute("data-src")
                if img_url:
                    images.append(img_url)
            
            product_detail['images'] = images
            
            # Trích xuất mô tả sản phẩm
            product_detail['description'] = self.get_text(".product-description")
            
            # Trích xuất thông số kỹ thuật
            specs = {}
            spec_rows = self.find_elements(".product-specifications tr")
            
            for row in spec_rows:
                try:
                    key = row.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text.strip()
                    value = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()
                    if key:
                        specs[key] = value
                except:
                    continue
            
            product_detail['specifications'] = specs
            
            return product_detail
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl chi tiết sản phẩm: {str(e)}")
            return None