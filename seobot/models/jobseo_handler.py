import os
import re
import asyncio
import logging
import datetime
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl
from scrapers import NormScraper, NewScraper
from review_generator import generate_review

logger = logging.getLogger(__name__)

# Конфигурация
ACCOUNTS = [
    {
        "name": "account_0",
        "api_id": 25568692,
        "api_hash": "709bb5b5f871c98a1d901b804f785667",
        "target_chat": "@jobseo_bot"
    },
]
TARGET_BOT = "@jobseo_bot"
MAX_CONCURRENT_ACCOUNTS = 5

class AccountManager:
    def __init__(self):
        self.clients = []
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_ACCOUNTS)
        self.account_data = {}
        self.account_clients = {}
        self.data_queue = asyncio.Queue()
        self.processed_today = 0

    async def init_accounts(self):
        """Инициализация всех аккаунтов"""
        for acc in ACCOUNTS:
            session_path = f"sessions/{acc['name']}"
            client = TelegramClient(
                session=session_path,
                api_id=acc["api_id"],
                api_hash=acc["api_hash"]
            )
            self.clients.append(client)
            self.account_clients[acc["name"]] = client
            self.account_data[acc["name"]] = {"direction": None, "address": None}

    async def run_selenium_in_executor(self, scraper_class, link):
        """Запускает Selenium в отдельном потоке"""
        loop = asyncio.get_running_loop()
        scraper = scraper_class(headless=True)
        return await loop.run_in_executor(None, scraper.run, link)

    def extract_link_from_message(self, message):
        """Извлекает ссылку из сообщения"""
        if not message.text:
            return None
            
        # 1. Проверяем сущности сообщения
        for entity in message.entities or []:
            if isinstance(entity, MessageEntityTextUrl):
                return entity.url
        
        # 2. Поиск URL в тексте
        url_match = re.search(r'https?://[^\s]+', message.text)
        return url_match.group(0) if url_match else None

    def extract_address_fallback(self, link: str) -> str:
        """Заглушка для обработки неизвестных ссылок"""
        logger.warning(f"Неизвестный тип ссылки: {link}")
        return "Адрес не определен"

    @staticmethod
    def extract_direction(text: str) -> str:
        """Извлекает направление из текста сообщения"""
        try:
            direction_match = re.search(r'Направление:\s*(.+)', text)
            return direction_match.group(1).strip() if direction_match else ""
        except Exception as e:
            logger.error(f"Ошибка извлечения направления: {str(e)}")
            return ""

    async def send_review(self, account_name: str, review_text: str) -> bool:
        """Отправляет отзыв через указанный аккаунт"""
        if account_name not in self.account_clients:
            logger.error(f"Аккаунт {account_name} не найден")
            return False
        
        client = self.account_clients[account_name]
        
        try:
            await client.send_message(TARGET_BOT, review_text)
            logger.info(f"[{account_name}] Отзыв отправлен")
            return True
        except Exception as e:
            logger.error(f"[{account_name}] Ошибка отправки: {str(e)}")
            return False

    async def start_work(self):
        """Начинает работу в 6 утра"""
        while True:
            now = datetime.datetime.now()
            if now.hour < 6:
                target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
                wait_seconds = (target_time - now).total_seconds()
                logger.info(f"Ждем до 6 утра: {wait_seconds} секунд")
                await asyncio.sleep(wait_seconds)
            
            logger.info("Начинаем работу!")
            await self.start()
            
            # Планируем следующий запуск на 6 утра следующего дня
            next_day = now + datetime.timedelta(days=1)
            next_target = next_day.replace(hour=6, minute=0, second=0, microsecond=0)
            wait_seconds = (next_target - datetime.datetime.now()).total_seconds()
            await asyncio.sleep(wait_seconds)

    async def start(self):
        """Запуск аккаунтов с ограничением"""
        tasks = []
        for client in self.clients:
            task = asyncio.create_task(self.run_account_with_throttle(client))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def run_account_with_throttle(self, client: TelegramClient):
        """Запускает аккаунт с ограничением"""
        async with self.semaphore:
            await self.handle_account(client)
            
    async def handle_account(self, client: TelegramClient):
        """Обработка аккаунта"""
        session_file = os.path.basename(client.session.filename)
        account_name = session_file.replace('.session', '')
        
        try:
            await client.start()
            logger.info(f"Аккаунт {account_name} авторизован")
            await client.send_message(TARGET_BOT, "Приступить к заданию ✍️")
            
            @client.on(events.NewMessage(from_users=TARGET_BOT))
            async def handler(event):
                await self.handle_bot_response(account_name, event.message)
                
            logger.info(f"[{account_name}] Обработчик запущен")
            while True:
                await asyncio.sleep(3600)

        except Exception as e:
            logger.error(f"Ошибка в аккаунте {account_name}: {str(e)}", exc_info=True)
        finally:
            await client.disconnect()

    async def handle_bot_response(self, account_name: str, message):
        """Обработка сообщений от бота"""
        try:
            text = message.text or ""
            logger.info(f"[{account_name}] Получено: {text[:50]}...")
            
            # 1. Обработка геолокации
            if "геолокацию" in text.lower():
                await message.reply("Тамбов")
                logger.info(f"[{account_name}] Город отправлен")
                return
            
            # 2. Извлечение и обработка ссылки
            if "прежде чем" in text.lower() or 'у вас есть' in text.lower():
                logger.info(f"[{account_name}] Извлекаю ссылку")
                link = self.extract_link_from_message(message)
                
                if link:
                    logger.info(f"[{account_name}] Ссылка: {link}")
                    
                    if link.startswith("https://teletype.in/"):
                        address = await self.run_selenium_in_executor(NormScraper, link)
                    elif link.startswith("https://jobseo.ru/"):
                        address = await self.run_selenium_in_executor(NewScraper, link)
                    else:
                        address = self.extract_address_fallback(link)
                    
                    # Обработка ошибок скрапинга
                    if address and not address.startswith(("BLOCKED_", "NETWORK_", "DRIVER_", "SCRAPER_")):
                        self.account_data[account_name]["address"] = address
                        logger.info(f"[{account_name}] Адрес сохранен: {address}")
                    else:
                        logger.warning(f"[{account_name}] Ошибка извлечения адреса: {address}")
                        # Повторная попытка через 10 секунд
                        await asyncio.sleep(10)
                        await message.reply("Продолжить выполнение ▶️")
                else:
                    logger.warning(f"[{account_name}] Ссылка не найдена")
                return
            # 3. Продолжение задания
            elif "незаконченное" in text.lower():
                await message.reply("Продолжить выполнение ▶️")
                logger.info(f"[{account_name}] Продолжил")
            
            # 4. Выбор платформы
            elif "выберите платформу" in text.lower():
                await message.reply("Yandex")
                logger.info(f"[{account_name}] Платформа отправлена")
            
            # 5. Сохранение направления
            elif "выбрали" in text.lower():
                direction = self.extract_direction(text)
                if direction:
                    self.account_data[account_name]["direction"] = direction
                    logger.info(f"[{account_name}] Направление: {direction}")
                await message.reply("Начать это задание")
                logger.info(f"[{account_name}] Задание принято")
            
            # 6. Запрос логина - финальный этап
            elif "логин" in text.lower():
                await asyncio.sleep(20)
                logger.info(f"[{account_name}] Запрос логина")
                
                account_data = self.account_data.get(account_name, {})
                address = account_data.get("address", "Неизвестный адрес")
                direction = account_data.get("direction", "Неизвестное направление")
                
                # Генерируем отзыв
                review = generate_review(address, direction)
                
                # Отправляем отзыв
                success = await self.send_review(account_name, review)
                
                if success:
                    await self.data_queue.put({
                        "account": account_name,
                        "address": address,
                        "direction": direction,
                        "review": review
                    })
                    self.processed_today += 1
                    logger.info(f"[{account_name}] Данные готовы")
                    
        except Exception as e:
            logger.error(f"[{account_name}] Ошибка: {str(e)}", exc_info=True)

    async def get_parsed_data(self):
        return await self.data_queue.get()
