from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time

EMAIL = ""
PASSWORD = ""

class BuildingsReport:
    def __init__(self, driver):
        self.driver = driver
        self.data = self.load_existing_data()
        self.new_data = []

    def load_existing_data(self):
        try:
            with open("buildings_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_first_title_from_data(self):
        if self.data:
            return self.data[0].get("Title")
        return None

    # Проверка на авторизацию
    def check_and_login(self):
        try:
            login_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='divUserStt']/a[@id='kct_login' and contains(@class, 're__btn-se-border--md')]"))
            )
            # Если кнопка найдена, значит нужно авторизоваться
            if login_button.is_displayed():
                login_button.click()
                time.sleep(30)

                try:
                    self.driver.switch_to.active_element.send_keys(Keys.TAB)
                    time.sleep(1)

                    # Ввод password
                    self.driver.switch_to.active_element.send_keys(PASSWORD)
                    time.sleep(2)
                    self.driver.switch_to.active_element.send_keys(Keys.SHIFT + Keys.TAB)
                    time.sleep(1)

                    # Ввод email
                    self.driver.switch_to.active_element.send_keys(EMAIL)
                    time.sleep(2)
                    
                    # Подтвердить авторизацию
                    self.driver.switch_to.active_element.send_keys(Keys.ENTER)
                    time.sleep(20)

                    # Закрыть всплывающее окно
                    self.driver.switch_to.active_element.send_keys(Keys.TAB)
                    time.sleep(2)
                    self.driver.switch_to.active_element.send_keys(Keys.ENTER)

                    time.sleep(20)
                    return True

                except Exception as e:
                    print(f"Ошибка при логине: {e}")
                    return False
                    
            else:
                print("Пользователь уже авторизован, продолжаю выполнение.")
                return True
            
        except Exception as e:
            print("Пользователь уже авторизован или кнопка 'Войти' не найдена.")
            return True

    def scrape_listings(self):
        self.driver.get("https://batdongsan.com.vn/nha-dat-cho-thue")
        
        while not self.check_and_login():
            print("Не удалось авторизоваться. Повторная попытка...")
        
        first_existing_title = self.get_first_title_from_data()
        max_pages = self.get_max_pages()
        current_page = 1
        
        while current_page <= max_pages:
            try:
                listings = self.get_listings()
                for listing_url in listings:
                    self.driver.get(listing_url)
                    time.sleep(2)

                    # Извлекаем данные
                    building_data = self.extract_building_data()

                    # Если JSON существует и заголовок совпадает с первым элементом, завершаем
                    if first_existing_title and building_data["Title"] == first_existing_title:
                        self.save_results()
                        return

                    # Если JSON отсутствует или заголовок не совпал, добавляем в новый список
                    self.new_data.append(building_data)

                    # Возвращаемся к списку
                    self.driver.back()

                # Переход на следующую страницу
                current_page += 1
                if not self.go_to_next_page(current_page):
                    break

            except Exception as e:
                print(f"Ошибка при обработке списка: {e}")
                break

        # Финальное сохранение данных
        self.save_results()

    def get_listings(self):
        try:
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.js__product-link-for-product-id'))
            )
            return [el.get_attribute('href') for el in elements]
        except TimeoutException:
            print("Ссылки на дома не найдены.")
            return []

    def get_max_pages(self):
        try:
            pagination_numbers = self.driver.find_elements(By.CSS_SELECTOR, ".re__pagination-group a.re__pagination-number")
            max_page = max(int(el.get_attribute("pid")) for el in pagination_numbers)
            return max_page
        except Exception as e:
            print(f"Ошибка при определении максимального числа страниц: {e}")
            return 1
    
    # Переход на следующую страницу
    def go_to_next_page(self, page_number):
        try:
            next_page_url = f"https://batdongsan.com.vn/nha-dat-cho-thue/p{page_number}"
            self.driver.get(next_page_url)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Ошибка при переходе на страницу {page_number}: {e}")
            return False

    def extract_building_data(self):
        return {
            "City": self.get_city(),
            "Date": self.get_date(),
            "Pets": self.get_pets(),
            "Size": self.get_size(),
            "Type": self.get_type(),
            "Email": self.get_email(),
            "Other": self.get_other(),
            "Rooms": self.get_rooms(),
            "Title": self.get_title(),
            "Images": self.get_images(),
            "Source": self.get_source(),
            "Videos": self.get_videos(),
            "Address": self.get_address(),
            "Balcony": self.get_balcony(),
            "Country": self.get_country(),
            "Deposit": self.get_deposit(),
            "Heating": self.get_heating(),
            "Parking": self.get_parking(),
            "ZipCode": self.get_zip_code(),
            "Bathroom": self.get_bathroom(),
            "Bedrooms": self.get_bedrooms(),
            "Currency": self.get_currency(),
            "District": self.get_district(),
            "Elevator": self.get_elevator(),
            "Location": self.get_location(),
            "Furnishing": self.get_furnishing(),
            "Year Built": self.get_year_built(),
            "Coordinates": self.get_coordinates(),
            "Description": self.get_description(),
            "Final price": self.get_final_price(),
            "Seller Name": self.get_seller_name(),
            "SubDistrict": self.get_sub_district(),
            "Floor Number": self.get_floor_number(),
            "Phone Number": self.get_phone_number(),
            "Contract Term": self.get_contract_term(),
            "Initial price": self.get_initial_price(),
            "Link to Viber": self.get_link_to_viber(),
            "Link to Seller": self.get_link_to_seller(),
            "Link to the ad": self.get_link_to_ad(),
            "Phone Number 2": self.get_phone_number_2(),
            "Link to Viber 2": self.get_link_to_viber_2(),
            "Washing machine": self.get_washing_machine(),
            "Link to Telegram": self.get_link_to_telegram(),
            "Link to WhatsApp": self.get_link_to_whatsapp(),
            "Availability Date": self.get_availability_date(),
            "Telegram Username": self.get_telegram_username(),
            "Link to Telegram 2": self.get_link_to_telegram_2(),
            "Link to WhatsApp 2": self.get_link_to_whatsapp_2(),
            "Telegram Username 2": self.get_telegram_username_2(),
            "Link to Facebook messenger": self.get_link_to_facebook_messenger()
        }

    def get_city(self):
        try:
            city = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='re__link-se' and @level='2']"))
            ).text
        except:
            city = None
        return city
    
    def get_date(self):
        try:
            date = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='re__pr-short-info-item js__pr-config-item']//span[@class='value']"))
            ).text
        except:
            date = None
        return date

    def get_pets(self):
        return None

    def get_size(self):
        try:
            size_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 're__pr-short-info-item') and contains(@class, 'js__pr-short-info-item')]//span[text()='Diện tích']/.."))
            )
            size_element = size_el.find_element(By.XPATH, ".//span[@class='value']")
            size = size_element.text
        except:
            size = None
        return size

    def get_type(self):
        return "House"

    def get_email(self):
        return None

    def get_other(self):
        result = {}
        try:
            container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='re__pr-specs-content js__other-info']"))
            )
            
            items = container.find_elements(By.XPATH, ".//div[contains(@class, 're__pr-specs-content-item')]")

            for item in items:
                try:
                    title = item.find_element(By.XPATH, ".//span[contains(@class, 're__pr-specs-content-item-title')]").text
                    value = item.find_element(By.XPATH, ".//span[contains(@class, 're__pr-specs-content-item-value')]").text

                    result[title] = value
                except Exception as e:
                    print(f"Error processing item: {e}")

        except Exception as e:
            print(f"Error finding container: {e}")

        return result

    def get_rooms(self):
        return self.get_bedrooms()

    def get_title(self):
        try:
            title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 're__pr-title pr-title js__pr-title')]")
            )).text
        except:
            title = None
        return title
    
    def get_images(self):
        try:
            media_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="re__media-thumbs js__media-thumbs"]'))
            )
            image_elements = media_container.find_elements(By.CSS_SELECTOR, 'div[data-filter="image"] img')
            image_urls = [img.get_attribute('data-src') for img in image_elements]
        except:
            image_urls = []
        return image_urls
    
    def get_source(self):
        return "batdongsan.com.vn"

    def get_videos(self):
        return None

    def get_address(self):
        try:
            address = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span.re__pr-short-description.js__pr-address'))
            ).text
        except:
            address = None
        return address
    
    def get_balcony(self):
        return None

    def get_country(self):
        return "Vietnam"

    def get_deposit(self):
        return None

    def get_heating(self):
        return None

    def get_parking(self):
        return None

    def get_zip_code(self):
        return None

    def get_bathroom(self):
        return None

    def get_bedrooms(self):
        try:
            bedrooms_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 're__pr-short-info-item') and contains(@class, 'js__pr-short-info-item')]//span[text()='Phòng ngủ']/.."))
            )
            bedrooms_element = bedrooms_el.find_element(By.XPATH, ".//span[@class='value']")
            bedrooms = bedrooms_element.text.split()[0]
        except:
            bedrooms = None
        return bedrooms
    
    def get_currency(self):
        return "VND"

    def get_district(self):
        try:
            district = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='re__link-se' and @level='3']"))
            ).text
        except:
            district = None
        return district

    def get_elevator(self):
        return None

    def get_location(self):
        return None

    def get_furnishing(self):
        return None

    def get_year_built(self):
        return None

    def get_coordinates(self):
        time.sleep(15)
        try:
            map_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@class='re__section re__pr-map js__section js__li-other']"
                ))
            )     
            self.driver.execute_script("arguments[0].scrollIntoView(true);", map_section)
            time.sleep(3)
            self.driver.execute_script("window.scrollBy(0, -100);")
            time.sleep(3)

            specific_section_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 're__section re__pr-map js__section js__li-other')]"))
            )

            section_body_div = specific_section_div.find_element(By.CLASS_NAME, "re__section-body")

            iframe = section_body_div.find_element(By.XPATH, ".//iframe[contains(@class, 'lazyloaded')]")

            data_src = iframe.get_attribute("data-src")

            coordinates = data_src.split("q=")[1].split("&")[0]

        except Exception as e:
            print(f"Ошибка: {e}")
            coordinates = None
        return coordinates

    def get_description(self):
        try:
            description = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 're__section-body.re__detail-content.js__section-body.js__pr-description.js__tracking'))
            ).text
        except:
            description = None
        return description

    def get_final_price(self):
        try:
            final_price = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 're__pr-short-info') and contains(@class, 'entrypoint-v1') and contains(@class, 'js__pr-short-info')]//span[@class='value']"))
            ).text
        except:
            final_price = None
        return final_price

    def get_seller_name(self):
        return None

    def get_sub_district(self):
        return None

    def get_floor_number(self):
        return None

    def get_phone_number(self):
        try:
            phone_under_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 're__btn') and contains(@class, 'js__phone-event')]"))
            )
            phone_under_button.click()
            time.sleep(5)
            
            phone_number_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 're__btn') and contains(@class, 'js__phone-event') and contains(@class, 'showHotline')]"))
            )
            phone_number = phone_number_div.get_attribute("mobile")

        except:
            phone_number = None
        return phone_number
    
    def get_contract_term(self):
        return None

    def get_initial_price(self):
        return self.get_final_price()

    def get_link_to_viber(self):
        return None

    def get_link_to_seller(self):
        return None

    def get_link_to_ad(self):
        return None

    def get_phone_number_2(self):
        return None

    def get_link_to_viber_2(self):
        return None

    def get_washing_machine(self):
        return None

    def get_link_to_telegram(self):
        return None

    def get_link_to_whatsapp(self):
        return None

    def get_availability_date(self):
        return None

    def get_telegram_username(self):
        return None

    def get_link_to_telegram_2(self):
        return None

    def get_link_to_whatsapp_2(self):
        return None

    def get_telegram_username_2(self):
        return None

    def get_link_to_facebook_messenger(self):
        return None

    def save_results(self):
        try:
            output_file = "buildings_data.json"
            if self.data:
                # Добавляем новые данные в начало существующего списка
                self.data = self.new_data + self.data
            else:
                # Если данных не было, сохраняем только новые
                self.data = self.new_data

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            print(f"Данные успешно сохранены в {output_file}")
        except Exception as e:
            print(f"Ошибка при сохранении данных: {str(e)}")
