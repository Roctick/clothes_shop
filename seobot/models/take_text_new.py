import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

GLOBAL_RESULT = None

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


    def _wait_for_page_load(self):
        """Ожидание загрузки страницы"""
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except TimeoutException:
            print("Страница не загрузилась вовремя")

    def get_element_text(self, selector, by=By.XPATH, timeout=10):
        """Получение текста элемента"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            return element.text
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Элемент не найден: {str(e)}")
            return None

    def check_page_parsable(self):
        """Проверка, можно ли спарсить страницу"""
        try:
            # Проверяем наличие основного контента
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*')))
            return True
        except TimeoutException:
            return False

    def run(self, url):
        global GLOBAL_RESULT
        
        """Основной метод выполнения скрапинга"""
        try:
            self.driver.get(url)
            self._wait_for_page_load()
            
            if not self.check_page_parsable():
                print("Страница не может быть спарсена")
                return
            
            # Получаем третий div на странице
            third_div_text = self.get_element_text('(//div)[3]')
            print(f"Текст третьего div: {third_div_text}")
            GLOBAL_RESULT = third_div_text
            
        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    # Проверка на тестовой страниц
    
    # Проверка на целевом URL
    scraper = WebScraper(headless=False)
    scraper.run("https://jobseo.ru/p/qElwGYRm50P4xQ36ZXynw2ljpRBDoVvq0A7v0LX1M8rxEkOw7j3PGB6l5Pkr0qZwj3KDpYG49Mm62OA0RMV2vlAG6rmkNLY57ExgD9GP63Okjg1l0MBnQpz4yJrb2GprY2PdWLDX7wKmV5Eq2oxRZNv8YAz1oqZ4Wwp3JOKy9nBQPXj8oLEvyz75JVgXl8nBNWQxR1RVoAnKzJpyQZqWD4m9Y2gNE9gkJWPKrxO8zGY14NLm5M8pW2vJ19zMn6j")