from pyrogram import Client, filters
from typing import Optional, List, Dict
from pyrogram.types import Message
import asyncio
import logging
import os
import re
import sys
import datetime

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Добавляем текущую директорию в путь Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Импорт функций парсинга
import take_text_new
import take_text_norm

# Импорт генератора отзывов
from review_generator import generate_review
# Конфигурация
ACCOUNTS = [
    {
        "name": "account_1",
        "api_id": 25258765,
        "api_hash": "25c2436c706409dcc02cbe6c475d820d"
    },
    {
        "name": "account_2", 
        "api_id": 29033861,
        "api_hash": "aa17ff0c511583dde361e5b3bd04389b"
    }
]
TARGET_BOT = "@jobseo_bot"
MAX_CONCURRENT_ACCOUNTS = 5  # Максимум одновременно работающих аккаунтов

data_queue = asyncio.Queue()

class AccountManager:
    def __init__(self):
        self.clients = []
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_ACCOUNTS)
        self.account_data = {}  # Хранение данных для каждого аккаунта
        self.account_clients = {}
        self.task_queues = {}  # Инициализировали словарь для очередей задач

    async def init_accounts(self):
        """Инициализация всех аккаунтов"""
        for acc in ACCOUNTS:
            client = Client(
                name=acc["name"],
                api_id=acc["api_id"],
                api_hash=acc["api_hash"],
                workdir="sessions"
            )
            self.clients.append(client)
            self.account_clients[acc["name"]] = client
            self.task_queues[acc["name"]] = asyncio.Queue()  # Теперь работает

    async def send_review(self, account_name: str, review_text: str) -> bool:
        """
        Отправляет отзыв через указанный аккаунт
        :param account_name: Имя аккаунта (сессии)
        :param review_text: Текст отзыва
        """
        if account_name not in self.account_clients:
            logger.error(f"Аккаунт {account_name} не найден для отправки отзыва")
            return False
        
        client = self.account_clients[account_name]
        
        try:
            if not client.is_connected:
                await client.start()
            await client.send_message(TARGET_BOT, review_text)
            logger.info(f"[{account_name}] Отзыв успешно отправлен")
            return True
        except Exception as e:
            logger.error(f"[{account_name}] Ошибка отправки отзыва: {str(e)}")
            return False
        
    async def start_work(self):
        """Начинает работу в 6 утра или сразу, если уже позже"""
        while True:
            now = datetime.datetime.now()
            if now.hour < 6:
                target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
                wait_seconds = (target_time - now).total_seconds()
                logger.info(f"Ждем до 6 утра: {wait_seconds} секунд")
                await asyncio.sleep(wait_seconds)
            
            logger.info("Начинаем работу!")
            await self.start()
            
            tomorrow = now + datetime.timedelta(days=1)
            next_target = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0)
            wait_seconds = (next_target - datetime.datetime.now()).total_seconds()
            await asyncio.sleep(wait_seconds)
        
    async def start(self):
        """Запуск аккаунтов с ограничением через семафор"""
        tasks = []
        for client in self.clients:
            task = asyncio.create_task(self.run_account_with_throttle(client))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def run_account_with_throttle(self, client: Client):
        """Запускает аккаунт с ограничением через семафор"""
        async with self.semaphore:
            await self.handle_account(client)

    @staticmethod
    def extract_link_from_message(text: str) -> Optional[str]:
        """Извлечение ссылки из текста сообщения"""
        try:
            match = re.search(r'\((https?://[^\s]+)\)', text)
            return match.group(1) if match else None
        except Exception as e:
            logger.error(f"Ошибка извлечения ссылки: {str(e)}")
            return None
        
    @staticmethod  # Исправлено: убран self
    def extract_direction(text: str) -> Optional[str]:
        """Извлекает направление из текста сообщения"""
        try:
            direction_match = re.search(r'Направление:\s*(.+)', text)
            return direction_match.group(1).strip() if direction_match else None
        except Exception as e:
            logger.error(f"Ошибка извлечения направления: {str(e)}")
            return None
        
    async def handle_account(self, client: Client):
        self.account_data[client.name] = {"direction": None, "address": None}

        try:
            await client.start()
            logger.info(f"Аккаунт {client.name} авторизован")
            await client.send_message(TARGET_BOT, "Приступить к заданию ✍️")
            
            @client.on_message(filters.bot & filters.user(TARGET_BOT))
            async def on_bot_message(_, message: Message):
                await self.handle_bot_response(client.name, message)
                
            while True:
                await asyncio.sleep(3600)

        except Exception as e:
            logger.error(f"Ошибка в аккаунте {client.name}: {str(e)}")
        finally:
            if client.name in self.account_data:
                del self.account_data[client.name]

    async def handle_bot_response(self, account_name: str, message: Message):
        """Обработка ответов бота"""
        try:
            text = message.text or ""
            
            if "геолокацию" in text.lower():
                await message.reply("Тамбов")
                logger.info(f"[{account_name}] Город отправлен")

            elif "незаконченное" in text.lower():
                await message.reply("Продолжить выполнение ▶️")
                logger.info(f"[{account_name}] Продолжил")
            
            elif "выберите платформу" in text.lower():
                await message.reply("2Gis")
                logger.info(f"[{account_name}] Платформа отправлена")
            
            if "выбрали задание" in text.lower():
                direction = self.extract_direction(text)
                if direction:
                    self.account_data[account_name]["direction"] = direction
                    logger.info(f"[{account_name}] Направление сохранено: {direction}")
                
                await message.reply("Начать это задание")
                logger.info(f"[{account_name}] Задание принято")
            
            elif "прежде чем" in text.lower():
                link = self.extract_link_from_message(text)
                if link:
                    logger.info(f"[{account_name}] Извлечена ссылка: {link}")
                    
                    try:
                        if link.startswith("https://teletype.in/"):
                            address = take_text_norm(link)
                        elif link.startswith("https://jobseo.ru/"):
                            address = take_text_new(link)
                        else:
                            raise ValueError("Неподдерживаемый тип ссылки")
                        
                        if address:
                            # Используем сохраненное направление
                            direction = self.account_data.get(account_name, {}).get("direction", "")
                            
                            # Генерируем отзыв
                            review = generate_review(address, direction)
                            
                            # Сохраняем в очередь
                            await data_queue.put({
                                "account": account_name,
                                "address": address,
                                "direction": direction,
                                "review": review
                            })
                            
                            logger.info(f"[{account_name}] Данные готовы: {address}, {direction}")
                            await message.reply("✅ Данные успешно обработаны! Ожидайте следующих инструкций.")
                        else:
                            logger.warning(f"[{account_name}] Адрес не найден")
                            await message.reply("❌ Адрес не найден")
                            
                    except Exception as e:
                        logger.exception(f"[{account_name}] Ошибка обработки ссылки: {str(e)}")
                        await message.reply("⚙️ Ошибка обработки данных")
        except Exception as e:
            logger.error(f"[{account_name}] Критическая ошибка: {str(e)}")


async def get_parsed_data():
    """Асинхронно получает данные из очереди"""
    return await data_queue.get()

async def main():
    manager = AccountManager()
    await manager.init_accounts()
    await manager.start_work()  # Используем start_work вместо start

if __name__ == "__main__":
    os.makedirs("sessions", exist_ok=True)
    asyncio.run(main())