# import os
# import json
# import csv
# import time
# import re
# from datetime import datetime
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from bs4 import BeautifulSoup

# from src.crawlers.base_crawler import BaseCrawler
# from src.config.settings import OUTPUT_DIR

# class TotoCatalogCrawler(BaseCrawler):
#     """
#         Crawler chuyên biệt để thu thập dữ liệu chi tiết từ danh sách sản phẩm TOTO
#         Args:
#             input_json_path (str): Đường dẫn đến file JSON đầu vào
#             output_dir (str, optional): Thư mục đầu ra tùy chỉnh. Mặc định là None.
#     """
    
    
#     def __init__(self, input_json_path, output_dir=None):
#         """Khởi tạo crawler với tên cụ thể và đường dẫn đến file JSON đầu vào"""
#         super().__init__(name="toto_catalog_crawler")
#         self.input_json_path = input_json_path
#         self.base_url = "https://tototuantu.vn"

#         if output_dir:
#             self.output_dir = output_dir
#         else:
#             self.output_dir = os.path.join("src/test", "toto_products")
        
#         # Thiết lập selectors cho tototuantu.vn (sử dụng từ TotoTuanTuCrawler)
#         self.selectors = {
#             'product_item': '.item_product_main',
#             'name': 'h1.title-product',  # Sửa thành h1.title-product
#             'price': '.price-box .special-price .price',
#             'original_price': '.price-box .old-price .price',
#             'image': '.product-gallery__image',
#             'specifications': '.specifications table tr',
#             'sku': '.product-sku',
#             'product_gallery': '.product-gallery',
#             'product_tabs': '.product-tabs',
#             'product_promotion': '.product-promotion',
#             'breadcrumb': '.breadcrumb a',
#             'slick_track': '.slick-track',  # Thêm selector cho slick-track
#             'img_fluid': '.img-fluid',  # Thêm selector cho img-fluid
#             'product_description': '.product_getcontent .content.js-content',  # Thêm selector cho mô tả chi tiết
#             'product_specifications': '.product-specifications .product_getcontent table tr',  # Thêm selector cho bảng thông số kỹ thuật
#             'product_features': '.product_getcontent .content.js-content ul li',  # Thêm selector cho tính năng sản phẩm
#             'product_technical_drawing': '.product_getcontent .content.js-content img',  # Thêm selector cho bản vẽ kỹ thuật
#             'product_links': '.product_getcontent .content.js-content a'  # Thêm selector cho các liên kết
#         }
        
#         # Tạo thư mục đầu ra nếu chưa tồn tại
#         if not os.path.exists(self.output_dir):
#             os.makedirs(self.output_dir)
#             self.logger.info(f"Đã tạo thư mục đầu ra: {self.output_dir}")
        
#         # Đọc dữ liệu từ file JSON đầu vào
#         self.products = self.load_input_json()
        
#     def load_input_json(self):
#         """Đọc dữ liệu từ file JSON đầu vào"""
#         try:
#             with open(self.input_json_path, 'r', encoding='utf-8') as f:
#                 products = json.load(f)
#             self.logger.info(f"Đã đọc {len(products)} sản phẩm từ file JSON đầu vào")
#             return products
#         except Exception as e:
#             self.logger.error(f"Lỗi khi đọc file JSON đầu vào: {str(e)}")
#             return []
    
#     def check_page_exists(self):
#         """Kiểm tra xem trang sản phẩm có tồn tại hay trả về lỗi 404"""
#         try:
#             # Tìm các chỉ báo lỗi 404
#             error_elements = self.find_elements("//div[contains(text(), 'TRANG KHÔNG ĐƯỢC TÌM THẤY')]", By.XPATH)
#             if error_elements:
#                 self.logger.error("Lỗi 404: Không tìm thấy trang sản phẩm")
#                 return False
                
#             # Kiểm tra sự hiện diện của nội dung sản phẩm để xác nhận trang tồn tại
#             product_element = self.find_element(".product-detail", wait_time=5)
#             return product_element is not None
#         except TimeoutException:
#             self.logger.error("Hết thời gian chờ trang sản phẩm tải")
#             return False
    
#     def get_text_from_element(self, parent_element, selector):
#         """
#         Lấy text từ phần tử con của parent_element (từ TotoTuanTuCrawler)
        
#         Args:
#             parent_element: Phần tử cha
#             selector (str): CSS selector của phần tử con
            
#         Returns:
#             str: Text của phần tử con
#         """
#         try:
#             element = parent_element.find_element(By.CSS_SELECTOR, selector)
#             return element.text.strip()
#         except:
#             return None
    
#     def extract_product_details(self, product_url, base_product_data):
#         """Thu thập thông tin chi tiết của sản phẩm từ URL"""
#         self.logger.info(f"Đang thu thập dữ liệu chi tiết cho sản phẩm: {product_url}")
        
#         # Khởi tạo dữ liệu sản phẩm với dữ liệu cơ bản từ JSON đầu vào
#         product_data = {
#             **base_product_data,
#             'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             'product_exists': False
#         }
        
#         try:
#             # Điều hướng đến trang sản phẩm
#             self.navigate_to(product_url)
            
#             # Kiểm tra xem trang sản phẩm có tồn tại không
#             if "TRANG KHÔNG ĐƯỢC TÌM THẤY" in self.driver.page_source:
#                 self.logger.warning(f"Trang sản phẩm không tồn tại: {product_url}")
#                 return product_data
        
#             # Sản phẩm tồn tại, cập nhật trạng thái
#             product_data["product_exists"] = True
        
#             # Thu thập tên sản phẩm
#             if not product_data.get('title'):
#                 product_data['title'] = self.get_text('.title-product')
#                 self.logger.info(f"Tên sản phẩm: {product_data.get('title')}")
        
#             # Thu thập mã sản phẩm và chuyển thành mảng
#             sku_array = self.extract_sku_as_array()
#             if sku_array:
#                 product_data["sku"] = sku_array[0]  # Lưu phần tử đầu tiên vào trường sku
#                 product_data["sku_array"] = sku_array  # Lưu toàn bộ mảng vào trường sku_array
            
#                 # Nếu có 2 phần tử trở lên, lưu riêng phần tử thứ 2 vào trường sku_additional
#                 if len(sku_array) > 1:
#                     product_data["sku_additional"] = sku_array[1]
        
#             # Thu thập mã sản phẩm (SKU)
#             if not product_data.get("sku") or product_data.get("sku") is None:
#                 sku_text = self.get_text(self.selectors['sku'])
#                 if sku_text:
#                     # Xử lý chuỗi SKU, loại bỏ "SKU:" nếu có
#                     sku = sku_text.replace("SKU:", "").strip()
#                     product_data["sku"] = sku
#                     self.logger.info(f"Mã sản phẩm: {sku}")
#                 else:
#                     # Thử trích xuất mã từ tên sản phẩm
#                     name = product_data.get('name', '')
#                     sku_match = re.search(r'[A-Z0-9]+-[A-Z0-9]+', name)
#                     product_data['sku'] = sku_match.group(0) if sku_match else None
            
#             # Thu thập thông số kỹ thuật
#             specs = self.extract_specifications()
#             if specs:
#                 product_data["specifications"] = specs
#                 self.logger.info(f"Đã thu thập {len(specs)} thông số kỹ thuật")
            
#             # Thu thập thông số kỹ thuật từ bảng riêng biệt
#             detailed_specs = self.extract_detailed_specifications()
#             if detailed_specs:
#                 # Nếu đã có specifications, hợp nhất với detailed_specs
#                 if product_data.get("specifications"):
#                     product_data["specifications"].update(detailed_specs)
#                 else:
#                     product_data["specifications"] = detailed_specs
#                 self.logger.info(f"Đã thu thập {len(detailed_specs)} thông số kỹ thuật chi tiết")
            
#             # Thu thập mô tả chi tiết sản phẩm
#             description_data = self.extract_product_description()
#             if description_data:
#                 product_data.update(description_data)
#                 self.logger.info("Đã thu thập mô tả chi tiết sản phẩm")
            
#             # Thu thập hình ảnh sản phẩm
#             images = self.extract_product_images()
#             if images:
#                 # Đảm bảo image_url chính đã có trong danh sách
#                 if product_data.get("image_url") and product_data["image_url"] not in images:
#                     images.insert(0, product_data["image_url"])
#                 product_data["all_images"] = images
#                 self.logger.info(f"Đã thu thập {len(images)} hình ảnh sản phẩm")
            
#             # Thu thập data-img từ các thẻ img có class img-fluid
#             data_img_urls = self.extract_data_img_from_slick_track()
#             if data_img_urls:
#                 product_data["data_img_urls"] = data_img_urls
#                 self.logger.info(f"Đã thu thập {len(data_img_urls)} URL từ thuộc tính data-img")
            
#             # Thu thập thông tin thêm (nếu có)
#             additional_info = self.extract_additional_info()
#             if additional_info:
#                 product_data["additional_info"] = additional_info
#                 self.logger.info("Đã thu thập thông tin bổ sung")
            
#             # Thu thập thông tin danh mục
#             breadcrumbs = self.find_elements(self.selectors['breadcrumb'])
#             if breadcrumbs and len(breadcrumbs) > 1:
#                 categories = []
#                 for breadcrumb in breadcrumbs[1:]:  # Bỏ qua "Trang chủ"
#                     categories.append(breadcrumb.text.strip())
#                 if categories:
#                     product_data["categories"] = categories
#                     self.logger.info(f"Danh mục: {', '.join(categories)}")
            
#             return product_data
            
#         except Exception as e:
#             self.logger.error(f"Lỗi khi thu thập dữ liệu sản phẩm: {str(e)}")
#             return product_data
    
#     def extract_product_description(self):
#         """
#         Trích xuất mô tả chi tiết sản phẩm từ phần nội dung
        
#         Returns:
#             dict: Dictionary chứa các thông tin mô tả chi tiết
#         """
#         description_data = {}
#         try:
#             # Tìm phần tử chứa mô tả chi tiết
#             description_element = self.find_element(self.selectors['product_description'])
#             if not description_element:
#                 self.logger.warning("Không tìm thấy phần tử mô tả chi tiết")
#                 return description_data
            
#             # Lấy toàn bộ nội dung HTML của phần mô tả
#             description_html = description_element.get_attribute("innerHTML")
#             if description_html:
#                 description_data["description_html"] = description_html
            
#             # Lấy nội dung text của phần mô tả
#             description_text = description_element.text.strip()
#             if description_text:
#                 description_data["description_text"] = description_text
            
#             # Trích xuất tính năng sản phẩm
#             features = []
#             feature_elements = self.find_elements(self.selectors['product_features'])
#             for feature in feature_elements:
#                 feature_text = feature.text.strip()
#                 if feature_text:
#                     features.append(feature_text)
            
#             if features:
#                 description_data["features"] = features
#                 self.logger.info(f"Đã thu thập {len(features)} tính năng sản phẩm")
            
#             # Trích xuất các liên kết trong mô tả
#             links = {}
#             link_elements = self.find_elements(self.selectors['product_links'])
#             for link in link_elements:
#                 link_text = link.text.strip()
#                 link_url = link.get_attribute("href")
#                 if link_text and link_url:
#                     links[link_text] = link_url
            
#             if links:
#                 description_data["related_links"] = links
#                 self.logger.info(f"Đã thu thập {len(links)} liên kết liên quan")
            
#             # Trích xuất bản vẽ kỹ thuật
#             technical_drawings = []
#             drawing_elements = self.find_elements(self.selectors['product_technical_drawing'])
#             for drawing in drawing_elements:
#                 drawing_url = drawing.get_attribute("src")
#                 if drawing_url:
#                     # Đảm bảo URL đầy đủ
#                     if drawing_url.startswith('//'):
#                         drawing_url = f"https:{drawing_url}"
#                     elif drawing_url.startswith('/'):
#                         drawing_url = f"{self.base_url}{drawing_url}"
                    
#                     technical_drawings.append(drawing_url)
            
#             if technical_drawings:
#                 description_data["technical_drawings"] = technical_drawings
#                 self.logger.info(f"Đã thu thập {len(technical_drawings)} bản vẽ kỹ thuật")
            
#             # Trích xuất thông tin chi tiết sản phẩm (nếu có)
#             product_details = {}
            
#             # Tìm các phần tử h2 làm tiêu đề
#             h2_elements = description_element.find_elements(By.TAG_NAME, "h2")
#             for i, h2 in enumerate(h2_elements):
#                 try:
#                     title = h2.text.strip()
#                     if not title:
#                         continue
                    
#                     # Phương pháp an toàn hơn để lấy nội dung sau tiêu đề
#                     content = ""
                    
#                     # Sử dụng JavaScript để lấy phần tử tiếp theo
#                     script = """
#                     function getNextSiblingContent(element) {
#                         let nextSibling = element.nextElementSibling;
#                         if (nextSibling) {
#                             return nextSibling.textContent.trim();
#                         }
#                         return "";
#                     }
#                     return getNextSiblingContent(arguments[0]);
#                     """
                    
#                     try:
#                         content = self.driver.execute_script(script, h2)
#                     except Exception as js_error:
#                         self.logger.warning(f"Không thể lấy nội dung bằng JavaScript: {str(js_error)}")
                        
#                         # Phương pháp dự phòng: tìm tất cả phần tử con của container và xác định vị trí
#                         try:
#                             all_elements = description_element.find_elements(By.XPATH, ".//*")
#                             h2_index = -1
                            
#                             # Tìm vị trí của h2 hiện tại
#                             for idx, elem in enumerate(all_elements):
#                                 if elem == h2:
#                                     h2_index = idx
#                                     break
                            
#                             # Nếu tìm thấy h2 và không phải phần tử cuối cùng
#                             if h2_index >= 0 and h2_index < len(all_elements) - 1:
#                                 next_elem = all_elements[h2_index + 1]
#                                 content = next_elem.text.strip()
#                         except Exception as backup_error:
#                             self.logger.warning(f"Phương pháp dự phòng cũng thất bại: {str(backup_error)}")
                    
#                     # Nếu có nội dung, thêm vào product_details
#                     if content:
#                         product_details[title] = content
#                         self.logger.info(f"Đã thu thập nội dung cho tiêu đề: {title}")
#                 except Exception as section_error:
#                     self.logger.warning(f"Lỗi khi xử lý phần tiêu đề {i}: {str(section_error)}")
            
#             if product_details:
#                 description_data["product_details"] = product_details
#                 self.logger.info(f"Đã thu thập {len(product_details)} phần thông tin chi tiết sản phẩm")
            
#             return description_data
            
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất mô tả chi tiết sản phẩm: {str(e)}")
#             return description_data
    
#     def extract_detailed_specifications(self):
#         """
#         Trích xuất thông số kỹ thuật chi tiết từ bảng thông số riêng biệt
        
#         Returns:
#             dict: Dictionary chứa các thông số kỹ thuật chi tiết
#         """
#         detailed_specs = {}
#         try:
#             # Tìm bảng thông số kỹ thuật chi tiết
#             spec_rows = self.find_elements(self.selectors['product_specifications'])
            
#             # Trích xuất dữ liệu từ các hàng
#             for row in spec_rows:
#                 try:
#                     cells = row.find_elements(By.TAG_NAME, "td")
#                     if len(cells) >= 2:
#                         key = cells[0].text.strip()
#                         value = cells[1].text.strip()
#                         if key:  # Chỉ thêm nếu key không trống
#                             detailed_specs[key] = value
#                 except Exception as e:
#                     self.logger.warning(f"Lỗi khi xử lý hàng thông số chi tiết: {str(e)}")
            
#             return detailed_specs
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất thông số kỹ thuật chi tiết: {str(e)}")
#             return {}
    
#     def extract_data_img_from_slick_track(self):
#         """
#         Trích xuất thuộc tính data-img từ các thẻ img có class img-fluid trong slick-track
        
#         Returns:
#             list: Mảng chứa các URL từ thuộc tính data-img
#         """
#         data_img_urls = []
#         try:
#             # Tìm tất cả các thẻ img có class img-fluid trong slick-track
#             slick_track = self.find_element(self.selectors['slick_track'])
#             if slick_track:
#                 img_elements = slick_track.find_elements(By.CSS_SELECTOR, self.selectors['img_fluid'])
#                 self.logger.info(f"Đã tìm thấy {len(img_elements)} thẻ img có class img-fluid trong slick-track")
                
#                 # Trích xuất thuộc tính data-img từ mỗi thẻ img
#                 for img in img_elements:
#                     data_img = img.get_attribute("data-img")
#                     if data_img:
#                         # Đảm bảo URL đầy đủ
#                         if data_img.startswith('//'):
#                             data_img = f"https:{data_img}"
#                         elif data_img.startswith('/'):
#                             data_img = f"{self.base_url}{data_img}"
                        
#                         # Thêm vào mảng kết quả nếu chưa có
#                         if data_img not in data_img_urls:
#                             data_img_urls.append(data_img)
#                             self.logger.info(f"Đã thêm URL từ data-img: {data_img}")
#             else:
#                 self.logger.warning("Không tìm thấy phần tử slick-track")
            
#             return data_img_urls
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất thuộc tính data-img: {str(e)}")
#             return data_img_urls
    
#     def extract_sku_as_array(self):
#         """
#         Trích xuất mã sản phẩm từ thẻ span và chuyển thành mảng nếu có dấu cách
        
#         Returns:
#             list: Mảng chứa các phần của mã sản phẩm
#         """
#         try:
#             # Tìm thẻ span chứa mã sản phẩm
#             sku_element = self.find_element(".status_name.product-sku")
#             if sku_element:
#                 # Lấy nội dung text
#                 sku_text = sku_element.text.strip()
#                 self.logger.info(f"Đã tìm thấy mã sản phẩm: {sku_text}")
                
#                 # Tách thành mảng nếu có dấu cách
#                 if " " in sku_text:
#                     sku_array = sku_text.split()
#                     self.logger.info(f"Đã tách mã sản phẩm thành: {sku_array}")
#                     return sku_array
#                 else:
#                     return [sku_text]
#             else:
#                 self.logger.warning("Không tìm thấy thẻ span chứa mã sản phẩm")
#                 return []
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất mã sản phẩm: {str(e)}")
#             return []
    
#     def extract_specifications(self):
#         """Trích xuất thông số kỹ thuật sản phẩm (sử dụng phương pháp từ TotoTuanTuCrawler)"""
#         specs = {}
#         try:
#             # Tìm bảng thông số kỹ thuật
#             spec_rows = self.find_elements(self.selectors['specifications'])
            
#             # Trích xuất dữ liệu từ các hàng
#             for row in spec_rows:
#                 try:
#                     cells = row.find_elements(By.TAG_NAME, "td")
#                     if len(cells) >= 2:
#                         key = cells[0].text.strip()
#                         value = cells[1].text.strip()
#                         if key:  # Chỉ thêm nếu key không trống
#                             specs[key] = value
#                 except Exception as e:
#                     self.logger.warning(f"Lỗi khi xử lý hàng thông số: {str(e)}")
            
#             return specs
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất thông số kỹ thuật: {str(e)}")
#             return {}
    
#     def extract_product_images(self):
#         """Trích xuất hình ảnh sản phẩm (sử dụng phương pháp từ TotoTuanTuCrawler)"""
#         images = []
#         try:
#             # Tìm tất cả các phần tử hình ảnh trong gallery
#             image_elements = self.find_elements(self.selectors['image'])
            
#             # Trích xuất URL hình ảnh
#             for img in image_elements:
#                 try:
#                     # Ưu tiên thuộc tính data-src (lazy loading) hoặc src
#                     img_url = img.get_attribute("src")
#                     if not img_url or img_url.endswith("blank.png"):
#                         img_url = img.get_attribute("data-src")
                    
#                     if img_url and not img_url.endswith('.svg') and "medium" not in img_url:  # Bỏ qua các icon SVG và ảnh thumbnail
#                         # Đảm bảo URL đầy đủ
#                         if img_url.startswith('/'):
#                             img_url = f"{self.base_url}{img_url}"
#                         if img_url not in images:  # Tránh trùng lặp
#                             images.append(img_url)
#                 except Exception as e:
#                     self.logger.warning(f"Lỗi khi xử lý hình ảnh: {str(e)}")
            
#             return images
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất hình ảnh sản phẩm: {str(e)}")
#             return []
    
#     def extract_additional_info(self):
#         """Trích xuất thông tin bổ sung như tính năng, ưu đãi, v.v."""
#         additional_info = {}
#         try:
#             # Tìm các tab thông tin bổ sung
#             tabs = self.find_elements(f"{self.selectors['product_tabs']} a")
            
#             for tab in tabs:
#                 try:
#                     tab_name = tab.text.strip()
#                     if tab_name and tab_name.lower() not in ['mô tả', 'thông số kỹ thuật']:
#                         # Click vào tab để hiển thị nội dung
#                         tab.click()
#                         time.sleep(1)
                        
#                         # Lấy nội dung tab
#                         tab_content = self.get_text("//div[contains(@class, 'tab-content') and contains(@class, 'active')]", By.XPATH)
#                         if tab_content:
#                             additional_info[tab_name] = tab_content
#                 except Exception as e:
#                     self.logger.warning(f"Lỗi khi xử lý tab {tab.text}: {str(e)}")
            
#             return additional_info
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất thông tin bổ sung: {str(e)}")
#             return {}
    
#     def process_all_products(self, limit=None):
#         """Xử lý tất cả sản phẩm từ danh sách đầu vào"""
#         results = []
#         total_products = len(self.products)
#         processed_count = 0
        
#         self.logger.info(f"Bắt đầu xử lý {total_products} sản phẩm")
        
#         for i, product in enumerate(self.products):
#             if limit and i >= limit:
#                 self.logger.info(f"Đã đạt đến giới hạn {limit} sản phẩm")
#                 break
                
#             self.logger.info(f"Đang xử lý sản phẩm {i+1}/{total_products}: {product.get('name', 'Không có tên')}")
            
#             try:
#                 # Thu thập thông tin chi tiết
#                 product_url = product.get('product_url')
#                 if not product_url:
#                     self.logger.warning(f"Sản phẩm {i+1} không có URL, bỏ qua")
#                     continue
                    
#                 detailed_product = self.extract_product_details(product_url, product)
#                 results.append(detailed_product)
#                 processed_count += 1
                
#                 # Lưu kết quả trung gian sau mỗi 5 sản phẩm
#                 if processed_count % 5 == 0:
#                     self.save_results(results)
#                     self.logger.info(f"Đã lưu kết quả trung gian sau khi xử lý {processed_count}/{total_products} sản phẩm")
                
#                 # Tạm dừng giữa các yêu cầu để tránh quá tải máy chủ
#                 time.sleep(2)
                
#             except Exception as e:
#                 self.logger.error(f"Lỗi khi xử lý sản phẩm {i+1}: {str(e)}")
        
#         # Lưu kết quả cuối cùng
#         if results:
#             self.save_results(results)
#             self.logger.info(f"Đã hoàn thành xử lý {processed_count}/{total_products} sản phẩm")
        
#         return results
    
#     def save_results(self, results):
#         """Lưu kết quả vào file JSON và CSV"""
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         # Lưu file JSON
#         json_filename = os.path.join(self.output_dir, f"toto_products_detailed_{timestamp}.json")
#         try:
#             with open(json_filename, 'w', encoding='utf-8') as f:
#                 json.dump(results, f, ensure_ascii=False, indent=2)
#             self.logger.info(f"Đã lưu kết quả vào file JSON: {json_filename}")
#         except Exception as e:
#             self.logger.error(f"Lỗi khi lưu file JSON: {str(e)}")
        
#         # Lưu file CSV
#         csv_filename = os.path.join(self.output_dir, f"toto_products_detailed_{timestamp}.csv")
#         try:
#             # Xác định tất cả các trường có thể có
#             fieldnames = set()
#             for product in results:
#                 for key in product.keys():
#                     if key not in ['specifications', 'additional_info', 'all_images', 'data_img_urls', 
#                                   'description_html', 'features', 'related_links', 'technical_drawings', 
#                                   'product_details', 'description_text']:
#                         fieldnames.add(key)
            
#             fieldnames = sorted(list(fieldnames))
            
#             with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
#                 writer = csv.DictWriter(f, fieldnames=fieldnames)
#                 writer.writeheader()
                
#                 for product in results:
#                     # Tạo bản sao của sản phẩm chỉ với các trường cơ bản
#                     product_copy = {}
#                     for key in fieldnames:
#                         if key in product:
#                             # Xử lý các trường đặc biệt
#                             if isinstance(product[key], list):
#                                 product_copy[key] = ', '.join(str(item) for item in product[key])
#                             elif isinstance(product[key], dict):
#                                 product_copy[key] = json.dumps(product[key], ensure_ascii=False)
#                             else:
#                                 product_copy[key] = product[key]
#                         else:
#                             product_copy[key] = ''
                    
#                     writer.writerow(product_copy)
            
#             self.logger.info(f"Đã lưu kết quả vào file CSV: {csv_filename}")
#         except Exception as e:
#             self.logger.error(f"Lỗi khi lưu file CSV: {str(e)}")
        
#         return json_filename, csv_filename

#     def extract_description_values(self, product_data):
#         """
#         Trích xuất giá trị từ các trường description_html và description_text
        
#         Args:
#             product_data (dict): Dữ liệu sản phẩm chứa các trường description
            
#         Returns:
#             list: Mảng chứa các giá trị đã trích xuất
#         """
#         result = []
        
#         # Trích xuất giá trị từ description_html nếu có
#         if 'description_html' in product_data:
#             result.append(product_data['description_html'])
        
#         # Trích xuất giá trị từ description_text nếu có
#         if 'description_text' in product_data:
#             result.append(product_data['description_text'])
        
#         return result
    
#     def extract_values_from_description_json(self, json_data):
#         """
#         Trích xuất giá trị từ chuỗi JSON chứa description_html và description_text
        
#         Args:
#             json_data (str): Chuỗi JSON chứa dữ liệu mô tả
            
#         Returns:
#             list: Mảng chứa các giá trị đã trích xuất
#         """
#         try:
#             # Phân tích chuỗi JSON
#             data = json.loads(json_data) if isinstance(json_data, str) else json_data
            
#             # Khởi tạo mảng kết quả
#             result = []
            
#             # Trích xuất giá trị từ description_html nếu có
#             if 'description_html' in data:
#                 result.append(data['description_html'])
            
#             # Trích xuất giá trị từ description_text nếu có
#             if 'description_text' in data:
#                 result.append(data['description_text'])
            
#             return result
#         except Exception as e:
#             self.logger.error(f"Lỗi khi trích xuất giá trị từ JSON: {str(e)}")
#             return []

# def main():
#     """Hàm chính để chạy crawler"""
#     import argparse
    
#     parser = argparse.ArgumentParser(description='TOTO Catalog Crawler')
#     parser.add_argument('--input', type=str, required=True, help='Đường dẫn đến file JSON đầu vào')
#     parser.add_argument('--limit', type=int, default=None, help='Giới hạn số lượng sản phẩm cần xử lý')
    
#     args = parser.parse_args()
    
#     # Khởi tạo crawler
#     crawler = TotoCatalogCrawler(args.input)
    
#     try:
#         # Xử lý tất cả sản phẩm
#         crawler.process_all_products(limit=args.limit)
#     except Exception as e:
#         crawler.logger.error(f"Lỗi trong quá trình xử lý: {str(e)}")
#     finally:
#         # Đóng trình duyệt
#         crawler.close()

# if __name__ == "__main__":
#     main()
import os
import json
import csv
import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

from src.crawlers.base_crawler import BaseCrawler
from src.config.settings import OUTPUT_DIR

class TotoCatalogCrawler(BaseCrawler):
    """
        Crawler chuyên biệt để thu thập dữ liệu chi tiết từ danh sách sản phẩm TOTO
        Args:
            input_json_path (str): Đường dẫn đến file JSON đầu vào
            output_dir (str, optional): Thư mục đầu ra tùy chỉnh. Mặc định là None.
    """
    
    
    def __init__(self, input_json_path, output_dir=None):
        """Khởi tạo crawler với tên cụ thể và đường dẫn đến file JSON đầu vào"""
        super().__init__(name="toto_catalog_crawler")
        self.input_json_path = input_json_path
        self.base_url = "https://tototuantu.vn"

        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join("src/test", "toto_products")
        
        # Thiết lập selectors cho tototuantu.vn (sử dụng từ TotoTuanTuCrawler)
        self.selectors = {
            'product_item': '.item_product_main',
            'name': 'h1.title-product',  # Sửa thành h1.title-product
            'price': '.price-box .special-price .price',
            'original_price': '.price-box .old-price .price',
            'image': '.product-gallery__image',
            'specifications': '.specifications table tr',
            'sku': '.product-sku',
            'product_gallery': '.product-gallery',
            'product_tabs': '.product-tabs',
            'product_promotion': '.product-promotion',
            'breadcrumb': '.breadcrumb a',
            'slick_track': '.slick-track',  # Thêm selector cho slick-track
            'img_fluid': '.img-fluid',  # Thêm selector cho img-fluid
            'product_description': '.product_getcontent .content.js-content',  # Thêm selector cho mô tả chi tiết
            'product_specifications': '.product-specifications .product_getcontent table tr',  # Thêm selector cho bảng thông số kỹ thuật
            'product_features': '.product_getcontent .content.js-content ul li',  # Thêm selector cho tính năng sản phẩm
            'product_technical_drawing': '.product_getcontent .content.js-content img',  # Thêm selector cho bản vẽ kỹ thuật
            'product_links': '.product_getcontent .content.js-content a',  # Thêm selector cho các liên kết
            'section_sec_tab': '.section.sec_tab',  # Thêm selector cho section sec_tab (không có khoảng trắng ở cuối)
            'see_more_button': '.js-seemore a',  # Nút "Xem thêm"
            'collapse_button': '.js-seemore a[title="Thu gọn"]',  # Nút "Thu gọn"
            'content_wrapper': '.js-content-wrapper'  # Phần tử chứa nội dung có thể mở rộng/thu gọn
        }
        
        # Tạo thư mục đầu ra nếu chưa tồn tại
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Đã tạo thư mục đầu ra: {self.output_dir}")
        
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
        """Thu thập thông tin chi tiết của sản phẩm từ URL"""
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
            product_data["product_exists"] = True
            
            # Thu thập HTML từ các phần tử có class "section sec_tab"
            section_tabs_html = self.extract_section_sec_tab_single_line_html()
            if section_tabs_html:
                product_data["section_tabs_html"] = section_tabs_html
                self.logger.info(f"Đã thu thập HTML từ {len(section_tabs_html)} phần tử có class 'section sec_tab'")
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Lỗi khi thu thập dữ liệu sản phẩm: {str(e)}")
            return product_data
    
    def extract_section_sec_tab_single_line_html(self):
        """
        Trích xuất HTML từ các phần tử có class "section sec_tab" và đặt tất cả trên một dòng
        
        Returns:
            list: Mảng chứa HTML của các phần tử có class "section sec_tab" trên một dòng
        """
        section_tabs_html = []
        try:
            # Tìm tất cả các phần tử có class "section sec_tab"
            section_elements = self.find_elements(self.selectors['section_sec_tab'])
            self.logger.info(f"Đã tìm thấy {len(section_elements)} phần tử có class 'section sec_tab'")
            
            # Trích xuất HTML từ mỗi phần tử
            for i, section in enumerate(section_elements):
                try:
                    # Sử dụng JavaScript để lấy HTML và loại bỏ các ký tự xuống dòng và tab
                    html_content = self.driver.execute_script("""
                        var element = arguments[0];
                        var html = element.outerHTML;
                        // Loại bỏ tất cả các ký tự xuống dòng và tab
                        html = html.replace(/\\n/g, '').replace(/\\t/g, '');
                        return html;
                    """, section)
                    
                    if html_content:
                        section_tabs_html.append(html_content)
                        self.logger.info(f"Đã trích xuất HTML từ phần tử section sec_tab thứ {i+1}")
                except Exception as e:
                    self.logger.warning(f"Lỗi khi trích xuất HTML từ phần tử section sec_tab thứ {i+1}: {str(e)}")
            
            return section_tabs_html
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất HTML từ các phần tử có class 'section sec_tab': {str(e)}")
            return section_tabs_html
    
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
                    if key not in ['specifications', 'additional_info', 'all_images', 'data_img_urls', 
                                  'description_html', 'features', 'related_links', 'technical_drawings', 
                                  'product_details', 'description_text', 'section_tabs_html']:
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

def process_specific_url(url, output_dir=None):
    """
    Xử lý một URL cụ thể thay vì đọc từ file JSON
    
    Args:
        url (str): URL của sản phẩm cần xử lý
        output_dir (str, optional): Thư mục đầu ra tùy chỉnh. Mặc định là None.
    """
    # Tạo một danh sách sản phẩm giả với URL được cung cấp
    dummy_products = [{"product_url": url, "name": "Sản phẩm từ URL"}]
    
    # Lưu danh sách sản phẩm giả vào file JSON tạm thời
    temp_json_path = "temp_product_url.json"
    with open(temp_json_path, 'w', encoding='utf-8') as f:
        json.dump(dummy_products, f, ensure_ascii=False)
    
    try:
        # Khởi tạo crawler với file JSON tạm thời
        crawler = TotoCatalogCrawler(temp_json_path, output_dir=output_dir)
        
        # Xử lý sản phẩm
        results = crawler.process_all_products()
        
        print(f"Đã hoàn thành việc trích xuất dữ liệu từ URL: {url}")
        return results
    except Exception as e:
        print(f"Lỗi khi xử lý URL {url}: {str(e)}")
        return None
    finally:
        # Xóa file JSON tạm thời
        if os.path.exists(temp_json_path):
            os.remove(temp_json_path)
        
def main():
    """Hàm chính để chạy crawler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TOTO Catalog Crawler')
    parser.add_argument('--input', type=str, help='Đường dẫn đến file JSON đầu vào')
    parser.add_argument('--url', type=str, help='URL cụ thể của sản phẩm cần xử lý')
    parser.add_argument('--output', type=str, default=None, help='Thư mục đầu ra cho kết quả')
    parser.add_argument('--limit', type=int, default=None, help='Giới hạn số lượng sản phẩm cần xử lý')
    
    args = parser.parse_args()
    
    if args.url:
        # Xử lý một URL cụ thể
        process_specific_url(args.url, output_dir=args.output)
    elif args.input:
        # Xử lý từ file JSON đầu vào
        crawler = TotoCatalogCrawler(args.input, output_dir=args.output)
        try:
            # Xử lý tất cả sản phẩm
            crawler.process_all_products(limit=args.limit)
            print("Đã hoàn thành việc trích xuất dữ liệu từ các phần tử có class 'section sec_tab'")
        except Exception as e:
            print(f"Lỗi trong quá trình xử lý: {str(e)}")
        finally:
            # Đóng trình duyệt
            crawler.close()
    else:
        print("Lỗi: Phải cung cấp --input hoặc --url")

if __name__ == "__main__":
    main()