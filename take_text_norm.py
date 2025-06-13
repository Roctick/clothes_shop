import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class WebScraper:
    def __init__(self, headless=False):
        self.options = webdriver.ChromeOptions()
        self._configure_options(headless)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, 15)

    def _configure_options(self, headless):
        """Настройка параметров браузера"""
        if headless:
            self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")

    def get_element_text(self, selector, by=By.XPATH, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, selector)))
            return element.text
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Элемент не найден: {str(e)}")
            return None

    def clean_address(self, text):
        """Очистка адреса от мусора"""
        if not text:
            return "Адрес не найден"
        return text.replace('2GIS', '').replace('2gis', '').strip()

    def run(self, url):
        try:
            self.driver.get(url)
            
            # Пример работы с адресом
            address = self.get_element_text('//h1[contains(text(), "Yandex Discovery")]')
            cleaned_address = self.clean_address(address)
            return cleaned_address  # Возвращаем результат вместо печати
            
        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
            return "Адрес не найден"
        finally:
            self.driver.quit()

if __name__ == "__main__":
    # Пример использования
    scraper = WebScraper(headless=True)
    