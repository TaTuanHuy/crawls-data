# src/crawlers/base_crawler.py
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager

from src.config.settings import SELENIUM_CONFIG, USER_AGENT, REQUEST_DELAY
from src.utils.logger import setup_logger

class BaseCrawler:
    """Lớp cơ sở cho các crawler sử dụng Selenium"""
    
    def __init__(self, name="base_crawler"):
        """Khởi tạo crawler với tên được chỉ định"""
        self.logger = setup_logger(name)
        self.driver = None
        self.wait = None
        self.initialize_driver()
    
    def initialize_driver(self):
        """Khởi tạo trình duyệt Selenium"""
        browser = SELENIUM_CONFIG.get('browser', 'firefox')
        headless = SELENIUM_CONFIG.get('headless', False)
        implicit_wait = SELENIUM_CONFIG.get('implicit_wait', 10)
        page_load_timeout = SELENIUM_CONFIG.get('page_load_timeout', 30)
        
        self.logger.info(f"Khởi tạo trình duyệt {browser} (headless: {headless})")
        
        if browser.lower() == 'firefox':
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument(f"user-agent={USER_AGENT}")
            
            self.driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )
        elif browser.lower() == 'chrome':
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument(f"user-agent={USER_AGENT}")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
        else:
            raise ValueError(f"Trình duyệt không được hỗ trợ: {browser}")
        
        # Thiết lập thời gian chờ
        self.driver.implicitly_wait(implicit_wait)
        self.driver.set_page_load_timeout(page_load_timeout)
        self.wait = WebDriverWait(self.driver, implicit_wait)
        
        self.logger.info("Trình duyệt đã được khởi tạo thành công")
    
    def navigate_to(self, url):
        """Điều hướng đến URL"""
        self.logger.info(f"Đang truy cập: {url}")
        self.driver.get(url)
        time.sleep(REQUEST_DELAY)  # Đợi trang tải
    
    def find_element(self, selector, by=By.CSS_SELECTOR, wait_time=None):
        """Tìm phần tử với selector"""
        try:
            if wait_time:
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((by, selector))
                )
            else:
                element = self.driver.find_element(by, selector)
            return element
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning(f"Không tìm thấy phần tử: {selector} - {str(e)}")
            return None
    
    def find_elements(self, selector, by=By.CSS_SELECTOR, wait_time=None):
        """Tìm tất cả phần tử với selector"""
        try:
            if wait_time:
                elements = WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_all_elements_located((by, selector))
                )
            else:
                elements = self.driver.find_elements(by, selector)
            return elements
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning(f"Không tìm thấy phần tử nào: {selector} - {str(e)}")
            return []
    
    def click_element(self, selector, by=By.CSS_SELECTOR, wait_time=None):
        """Click vào phần tử"""
        element = self.find_element(selector, by, wait_time)
        if element:
            try:
                element.click()
                time.sleep(REQUEST_DELAY)  # Đợi sau khi click
                return True
            except Exception as e:
                self.logger.error(f"Lỗi khi click vào phần tử {selector}: {str(e)}")
        return False
    
    def get_text(self, selector, by=By.CSS_SELECTOR, default=""):
        """Lấy text của phần tử"""
        element = self.find_element(selector, by)
        if element:
            return element.text.strip()
        return default
    
    def get_attribute(self, selector, attribute, by=By.CSS_SELECTOR, default=""):
        """Lấy thuộc tính của phần tử"""
        element = self.find_element(selector, by)
        if element:
            return element.get_attribute(attribute) or default
        return default
    
    def scroll_to_bottom(self, scroll_pause_time=1, max_scrolls=None):
        """Cuộn xuống cuối trang để tải thêm nội dung"""
        self.logger.info("Đang cuộn xuống để tải thêm nội dung...")
        
        # Lấy chiều cao ban đầu
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        
        while True:
            # Cuộn xuống cuối trang
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Đợi để trang tải thêm nội dung
            time.sleep(scroll_pause_time)
            scrolls += 1
            
            # Tính chiều cao mới
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Nếu chiều cao không thay đổi, đã đến cuối trang
            if new_height == last_height:
                self.logger.info("Đã đến cuối trang!")
                break
                
            # Nếu đã cuộn đủ số lần tối đa
            if max_scrolls and scrolls >= max_scrolls:
                self.logger.info(f"Đã cuộn {max_scrolls} lần!")
                break
                
            last_height = new_height
    
    def load_more_content(self, load_more_selector, max_clicks=5, by=By.CSS_SELECTOR):
        """Click nút 'Tải thêm' nhiều lần để lấy thêm nội dung"""
        clicks = 0
        
        while clicks < max_clicks:
            try:
                # Tìm nút "Tải thêm"
                load_more_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by, load_more_selector))
                )
                
                # Cuộn đến nút
                self.driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
                time.sleep(1)
                
                # Click nút
                load_more_button.click()
                self.logger.info(f"Đã click nút 'Tải thêm' lần thứ {clicks + 1}")
                
                # Đợi nội dung tải
                time.sleep(REQUEST_DELAY)
                clicks += 1
                
            except TimeoutException:
                self.logger.info("Không tìm thấy nút 'Tải thêm' hoặc đã tải hết nội dung")
                break
            except Exception as e:
                self.logger.error(f"Lỗi khi click nút 'Tải thêm': {str(e)}")
                break
    
    def handle_pagination(self, next_page_selector, max_pages=None, by=By.CSS_SELECTOR):
        """Xử lý phân trang bằng cách click vào nút 'Trang tiếp theo'"""
        page = 1
        
        while True:
            # Trích xuất dữ liệu từ trang hiện tại
            yield page
            
            # Kiểm tra giới hạn số trang
            if max_pages and page >= max_pages:
                self.logger.info(f"Đã đạt đến giới hạn số trang: {max_pages}")
                break
            
            # Click vào nút "Trang tiếp theo"
            next_button = self.find_element(next_page_selector, by)
            if next_button and next_button.is_displayed() and next_button.is_enabled():
                try:
                    next_button.click()
                    page += 1
                    self.logger.info(f"Đã chuyển đến trang {page}")
                    time.sleep(REQUEST_DELAY)  # Đợi trang tải
                except Exception as e:
                    self.logger.error(f"Lỗi khi chuyển trang: {str(e)}")
                    break
            else:
                self.logger.info("Đã đến trang cuối cùng hoặc không tìm thấy nút 'Trang tiếp theo'")
                break
    
    def take_screenshot(self, filename):
        """Chụp ảnh màn hình"""
        try:
            filepath = os.path.join(OUTPUT_DIR, filename)
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Đã chụp ảnh màn hình: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Lỗi khi chụp ảnh màn hình: {str(e)}")
            return None
    
    def close(self):
        """Đóng trình duyệt"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Đã đóng trình duyệt!")