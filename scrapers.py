import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class BaseScraper:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        self._configure_options(headless)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
    
    def _configure_options(self, headless):
        if headless:
            self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
    
    def _wait_for_page_load(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except TimeoutException:
            print("Страница не загрузилась вовремя")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
    
    def get_element_text(self, selector, by=By.XPATH, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            return element.text
        except Exception as e:
            print(f"Error while getting element text: {str(e)}")
            return None
        except (TimeoutException, NoSuchElementException):
            return None
    
    def close(self):
        self.driver.quit()

class NormScraper(BaseScraper):
    """Скрапер для извлечения адреса из H1 (после дефиса)"""
    
    def extract_h1(self):
        try:
            h1_element = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, 'h1'))
            )
            return h1_element.text.strip()
        except TimeoutException:
            return "H1 не найден"
        except Exception as e:
            return f"Ошибка при извлечении H1: {str(e)}"
        except TimeoutException:
            return "H1 не найден"
    
    def extract_text_after_dash(self, text):
        """Извлекает текст после первого знака '-' в строке"""
        if " - " in text:
            parts = text.split(" - ", 1)
            return parts[1].strip() if len(parts) > 1 else text
        elif "-" in text:
            parts = text.split("-", 1)
            return parts[1].strip() if len(parts) > 1 else text
        else:
            return text
    
    def run(self, url):
        """Основной метод выполнения"""
        try:
            self.driver.get(url)
            self._wait_for_page_load()
            
            # Извлекаем текст H1
            h1_text = self.extract_h1()
            if "H1 не найден" in h1_text:
                return h1_text
            
            # Извлекаем текст после дефиса
            result = self.extract_text_after_dash(h1_text)
            return result
        except Exception as e:
            return f"Ошибка в NormScraper: {str(e)}"
        finally:
            self.close()

class NewScraper(BaseScraper):
    """Скрапер для извлечения адреса из третьего div"""
    
    def run(self, url):
        try:
            self.driver.get(url)
            self._wait_for_page_load()
            
            # Получаем третий div на странице
            third_div_text = self.get_element_text('(//div)[3]')
            return third_div_text if third_div_text else "Адрес не найден"
        except Exception as e:
            return f"Ошибка в NewScraper: {str(e)}"
        finally:
            self.close()