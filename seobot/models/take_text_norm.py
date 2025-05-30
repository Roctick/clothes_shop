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
        """Основной метод выполнения скрапинга"""
        try:
            self.driver.get(url)
            
            # Пример работы с адресом
            address = self.get_element_text('//h1[contains(text(), "2GIS")]')
            cleaned_address = self.clean_address(address)
            print(f"Обработанный адрес: {cleaned_address}")
            
            # Дополнительные операции...
            
        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    # Пример использования
    scraper = WebScraper(headless=True)
    scraper.run("https://jobseo.ru/p/qElwGYRm50P4xQ36ZXynw2ljpRBDoVvq0A7v0LX1M8rxEkOw7j3PGB6l5Pkr0qZwj3KDpYG49Mm62OA0RMV2vlAG6rmkNLY57ExgD9GP63Okjg1l0MBnQpz4yJrb2GprY2PdWLDX7wKmV5Eq2oxRZNv8YAz1oqZ4Wwp3JOKy9nBQPXj8oLEvyz75JVgXl8nBNWQxR1RVoAnKzJpyQZqWD4m9Y2gNE9gkJWPKrxO8zGY14NLm5M8pW2vJ19zMn6j")  