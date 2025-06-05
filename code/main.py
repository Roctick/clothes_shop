import asyncio
import logging
import re
import random
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant, FloodWait, RPCError
from pyrogram.handlers import MessageHandler
import aiohttp
from pyrogram.types import Message, InlineKeyboardButton
from pyrogram.errors import UserAlreadyParticipant, FloodWait, RPCError, UserNotParticipant
from pyrogram.handlers import MessageHandler
# Глобальные настройки
RUNNING = True  # Флаг работы программы
START_TIME = time.time()  # Время старта программы
MAX_RUNTIME = 48 * 3600  # 48 часов работы

# Настройка логирования в файл
logging.basicConfig(
    filename='earn_bot.log',
    filemode='a',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())  # Вывод в консоль 

class AccountWorker:
    def __init__(self, session_name, api_id, api_hash):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.app = Client(session_name, api_id, api_hash)
        self.target_bot = "StarsovEarnBot"
        self.error_count = 0
        self.max_errors = 10
        self.http_session = None  # Сессия aiohttp
        
        # Регистрация обработчиков
        self.app.add_handler(MessageHandler(
            self.handle_bot_message, 
            filters.bot & filters.private
        ))

    async def safe_sleep(self, delay):
        while delay > 0 and RUNNING:
            chunk = min(delay, 5)
            await asyncio.sleep(chunk)
            delay -= chunk

    async def init_http_session(self):
        """Инициализация HTTP-сессии"""
        if not self.http_session:
            self.http_session = aiohttp.ClientSession()

    async def close_http_session(self):
        """Закрытие HTTP-сессии"""
        if self.http_session:
            await self.http_session.close()
            self.http_session = None

    async def open_flyer_link(self, url: str):
        """Выполнение GET-запроса к целевой ссылке"""
        try:
            await self.init_http_session()
            async with self.http_session.get(url) as response:
                if response.status == 200:
                    logger.info(f"[{self.session_name}] Успешно открыта ссылка: {url}")
                else:
                    logger.warning(f"[{self.session_name}] Ошибка при открытии ссылки: HTTP {response.status}")
        except Exception as e:
            logger.error(f"[{self.session_name}] Ошибка запроса: {e}")

    async def process_flyer_links(self, message: Message):
        """Поиск и обработка ссылок flyerservice в сообщении"""
        try:
            # Поиск ссылок в тексте сообщения
            text = message.text or ""
            flyer_links = re.findall(r'https?://api\.flyerservice\.io[^\s]+', text)
            
            # Поиск ссылок в кнопках
            if message.reply_markup:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        if hasattr(button, "url") and button.url:
                            if re.match(r'https?://api\.flyerservice\.io', button.url):
                                flyer_links.append(button.url)
            
            # Обработка найденных ссылок
            for link in set(flyer_links):  # Убираем дубликаты
                await self.safe_sleep(random.uniform(0.5, 1.5))
                await self.open_flyer_link(link)
                await self.safe_sleep(1.0)
                
            return bool(flyer_links)
        except Exception as e:
            logger.error(f"[{self.session_name}] Ошибка обработки ссылок: {e}")
            return False
        
    
    async def add_bot_to_chat(self, message: Message):
        """Добавляет бота в чат по команде"""
        try:
            logger.info(f"[{self.session_name}] Обнаружена команда добавления бота")
            
            # 1. Поиск кнопки с добавлением бота
            add_button = None
            if message.reply_markup and message.reply_markup.inline_keyboard:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        btn_text = button.text or ""
                        if any(kw in btn_text.lower() for kw in ["добавить", "добавьте", "пригласить"]):
                            add_button = button
                            break
                    if add_button:
                        break
            
            if not add_button:
                logger.warning(f"[{self.session_name}] Кнопка добавления бота не найдена")
                return False

            # 2. Извлечение информации о боте
            bot_username = None
            if isinstance(add_button, InlineKeyboardButton) and add_button.url:
                # Парсим URL для получения username бота
                match = re.search(r't.me/(\w+)', add_button.url)
                if match:
                    bot_username = match.group(1)
            
            if not bot_username:
                # Попробуем найти username в тексте сообщения
                match = re.search(r'@(\w+)', message.text or "")
                if match:
                    bot_username = match.group(1)
            
            if not bot_username:
                logger.warning(f"[{self.session_name}] Не удалось определить username бота")
                return False

            # 3. Добавление бота в чат
            try:
                # Проверяем, добавлен ли бот уже в чат
                try:
                    chat_member = await self.app.get_chat_member(message.chat.id, bot_username)
                    if chat_member:
                        logger.info(f"[{self.session_name}] Бот @{bot_username} уже в чате")
                        return True
                except UserNotParticipant:
                    pass
                
                # Добавляем бота
                await self.app.add_chat_members(message.chat.id, bot_username)
                logger.info(f"[{self.session_name}] Бот @{bot_username} успешно добавлен в чат")
                
                # Случайная задержка
                await self.safe_sleep(random.uniform(2.0, 4.0))
                return True
            except Exception as e:
                logger.error(f"[{self.session_name}] Ошибка добавления бота: {e}")
                return False
            
        except Exception as e:
            logger.error(f"[{self.session_name}] Ошибка обработки команды добавления: {e}")
            return False

    async def safe_sleep(self, delay):
        """Безопасный sleep с проверкой флага RUNNING"""
        while delay > 0 and RUNNING:
            chunk = min(delay, 5)  # Проверяем состояние каждые 5 сек
            await asyncio.sleep(chunk)
            delay -= chunk

    async def solve_captcha(self, message: Message):
        """Универсальный решатель капч с задержками"""
        try:
            # Случайная задержка перед действием
            await self.safe_sleep(random.uniform(1.0, 2.5))
            
            text_lower = message.text.lower()
            if not any(kw in text_lower for kw in ["изображен", "выберите", "нажмите"]) or not message.reply_markup:
                return False

            # Расширенный словарь для распознавания
            TARGETS = {
                "клубник": ("🍓", ["клубник", "ягод"]),
                "яблок": ("🍎", ["яблок", "ябл"]),
                "вишн": ("🍒", ["вишн", "черешн"]),
                "банан": ("🍌", ["банан"]),
                "виноград": ("🍇", ["виноград"]),
                "арбуз": ("🍉", ["арбуз"]),
                "лимон": ("🍋", ["лимон"]),
                "персик": ("🍑", ["персик"]),
                "груш": ("🍐", ["груш"]),
                "апельсин": ("🍊", ["апельсин"]),
                "помидор": ("🍅", ["помидор", "томат"]),
                "баклажан": ("🍆", ["баклажан"]),
                "капуст": ("🥬", ["капуст"]),
                "салат": ("🥬", ["салат", "латук"]),
                "брокколи": ("🥦", ["брокколи"]),
                "морков": ("🥕", ["морков"]),
                "огурец": ("🥒", ["огурец"]),
                "картош": ("🥔", ["картош", "картофел"]),
                "авокадо": ("🥑", ["авокадо"]),
                "кукуруз": ("🌽", ["кукуруз", "маис"]),
                "перец": ("🫑", ["перец", "перч"]),
                "чеснок": ("🧄", ["чеснок"]),
                "лук": ("🧅", ["лук"]),
                "арахис": ("🥜", ["арахис", "орех"]),
                "кокос": ("🥥", ["кокос"]),
                "киви": ("🥝", ["киви"]),
                "манго": ("🥭", ["манго"]),
                "хлеб": ("🍞", ["хлеб"]),
                "круасан": ("🥐", ["круасан"]),
                "сыр": ("🧀", ["сыр"]),
                "бургер": ("🍔", ["бургер"]),
                "пицца": ("🍕", ["пицца"]),
                "пончик": ("🍩", ["пончик"]),
                "печенье": ("🍪", ["печенье"]),
            }

            # Определяем объект капчи
            target_key = next((k for k in TARGETS if k in text_lower), None)
            if not target_key:
                logger.warning(f"[{self.session_name}] Неизвестный объект в капче: {message.text}")
                return False

            emoji, keywords = TARGETS[target_key]

            # Ищем подходящую кнопку
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    btn_text = button.text or ""
                    btn_lower = btn_text.lower()
                    # Проверяем по эмодзи или ключевым словам
                    if (emoji and emoji in btn_text) or any(kw in btn_lower for kw in keywords):
                        await message.click(button.text)
                        logger.info(f"[{self.session_name}] Капча решена: {btn_text}")
                        return True
                        
            logger.warning(f"[{self.session_name}] Кнопка для капчи не найдена")
            return False
        except Exception as e:
            logger.error(f"[{self.session_name}] Ошибка решения капчи: {e}")
            return False

    async def join_by_invite_link(self, invite_link: str):
        """Универсальный метод вступления по инвайт-ссылке"""
        try:
            # Случайная задержка перед действием
            await self.safe_sleep(random.uniform(1.5, 3.0))
            
            # Попробуем метод для публичных чатов
            if "/+" in invite_link:
                invite_hash = invite_link.split("/+")[1].split("?")[0]
                try:
                    await self.app.join_chat(f"+{invite_hash}")
                    logger.info(f"[{self.session_name}] Успешно вступили по инвайту: +{invite_hash}")
                    return True
                except UserAlreadyParticipant:
                    logger.info(f"[{self.session_name}] Уже участвуем в этом чате")
                    return True
                except Exception as e:
                    logger.error(f"[{self.session_name}] Ошибка при прямом вступлении: {e}")
                    
            # Альтернативный метод через получение чата по ссылке
            try:
                chat = await self.app.get_chat(invite_link)
                await self.app.join_chat(chat.id)
                logger.info(f"[{self.session_name}] Успешно вступили через get_chat: {chat.title}")
                return True
            except UserAlreadyParticipant:
                logger.info(f"[{self.session_name}] Уже участвуем в этом чате")
                return True
            except Exception as e:
                logger.error(f"[{self.session_name}] Ошибка при вступлении через get_chat: {e}")
                
            return False
        except Exception as e:
            logger.error(f"[{self.session_name}] Критическая ошибка при вступлении: {e}")
            return False

    async def process_task(self, message: Message):
        """Обрабатывает задание на подписку с задержками"""
        try:
            # 1. Находим кнопку перехода
            join_button = None
            if message.reply_markup and message.reply_markup.inline_keyboard:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        btn_text = button.text or ""
                        if "перейти" in btn_text.lower() and "🔎" in btn_text:
                            join_button = button
                            break
                    if join_button:
                        break
            
            if not join_button or not hasattr(join_button, "url"):
                logger.warning(f"[{self.session_name}] Кнопка перехода не найдена")
                return False

            url = join_button.url
            logger.info(f"[{self.session_name}] Обработка ссылки: {url}")

            # 2. Обрабатываем разные типы ссылок
            if "start=" in url:  # Боты с параметром
                match = re.search(r"t.me/(\w+)\?start=(\w+)", url)
                if match:
                    await self.safe_sleep(random.uniform(1.0, 2.0))
                    await self.app.send_message(match.group(1), f"/start {match.group(2)}")
                    logger.info(f"[{self.session_name}] Запущен бот: {match.group(1)} с параметром {match.group(2)}")
                else:
                    logger.warning(f"[{self.session_name}] Не удалось разобрать ссылку на бота: {url}")
            else:
                # Для всех остальных случаев используем универсальный метод
                await self.join_by_invite_link(url)

            # Задержка перед подтверждением
            await self.safe_sleep(random.uniform(3.0, 5.0))

            # 3. Подтверждаем выполнение
            confirm_button = None
            if message.reply_markup and message.reply_markup.inline_keyboard:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        btn_text = button.text or ""
                        if any(kw in btn_text.lower() for kw in ["подтвердить", "проверить"]):
                            confirm_button = button
                            break
                    if confirm_button:
                        break
            
            if confirm_button:
                await self.safe_sleep(random.uniform(1.0, 2.0))
                await message.click(confirm_button.text)
                logger.info(f"[{self.session_name}] Подтверждение отправлено")
                return True
            else:
                logger.warning(f"[{self.session_name}] Кнопка подтверждения не найдена")
                return False
                
        except Exception as e:
            logger.error(f"[{self.session_name}] Ошибка обработки задания: {e}")
            return False
        
    async def start_bot(self, message: Message):
        """Запуск бота по команде с обработкой ссылок с параметрами"""
        try:
            # Случайная задержка перед действием
            await self.safe_sleep(random.uniform(1.0, 2.5))
            
            # 1. Поиск всех возможных ссылок в сообщении
            bot_links = []
            text = message.text or ""
            
            # Поиск в тексте сообщения
            text_links = re.findall(r'https?://t\.me/(\w+)(?:\?start=(\w+))?', text)
            for match in text_links:
                bot_links.append({
                    "username": match[0],
                    "param": match[1] if len(match) > 1 else None
                })
            
            # Поиск в кнопках
            if message.reply_markup:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        if hasattr(button, "url") and button.url:
                            match = re.search(r't\.me/(\w+)(?:\?start=(\w+))?', button.url)
                            if match:
                                bot_links.append({
                                    "username": match.group(1),
                                    "param": match.group(2) if match.lastindex > 1 else None
                                })
            
            if not bot_links:
                logger.warning(f"[{self.session_name}] Не удалось найти ссылку на бота")
                return False
            
            # 2. Запускаем всех найденных ботов
            for bot_link in bot_links:
                username = bot_link["username"]
                param = bot_link["param"]
                
                try:
                    # Формируем команду запуска
                    command = f"/start {param}" if param else "/start"
                    
                    logger.info(f"[{self.session_name}] Запускаем бота: @{username} с командой '{command}'")
                    await self.app.send_message(username, command)
                    
                    # Случайная задержка между запусками
                    await self.safe_sleep(random.uniform(1.5, 3.0))
                    
                except RPCError as e:
                    logger.error(f"[{self.session_name}] Ошибка запуска @{username}: {e}")
            
            # 3. Подтверждаем выполнение
            confirm_button = None
            if message.reply_markup:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        btn_text = button.text or ""
                        if any(kw in btn_text.lower() for kw in ["подтвердить", "готово", "я запустил"]):
                            confirm_button = button
                            break
                    if confirm_button:
                        break
            
            if confirm_button:
                await self.safe_sleep(random.uniform(2.0, 4.0))
                await message.click(confirm_button.text)
                logger.info(f"[{self.session_name}] Подтверждение отправлено")
            else:
                logger.warning(f"[{self.session_name}] Кнопка подтверждения не найдена")
            
            return True
            
        except RPCError as e:
            logger.error(f"[{self.session_name}] Ошибка при запуске бота: {e}")
            return False
        except Exception as e:
            logger.exception(f"[{self.session_name}] Критическая ошибка в start_bot: {e}")
            return False

    async def handle_bot_message(self, client, message: Message):
        """Обработка входящих сообщений"""
        try:
            if not message.from_user or message.from_user.username != self.target_bot:
                return

            text = message.text or ""
            
            # Обработка flyer-ссылок в первую очередь
            if await self.process_flyer_links(message):
                return
            elif "запустите" in text.lower():
                await self.start_bot(message)
            elif "добавьте" in text.lower():
                await self.add_bot_to_chat(message)
            elif any(kw in text.lower() for kw in ["изображен", "выберите", "нажмите"]):
                await self.solve_captcha(message)
            elif any(kw in text.lower() for kw in ["подпишитесь", "задание"]):
                await self.process_task(message)
        except Exception as e:
            logger.error(f"[{self.session_name}] Ошибка обработки: {e}")

    async def main_loop(self):
        """Основной цикл для аккаунта"""
        async with self.app:
            logger.info(f"[{self.session_name}] Аккаунт запущен")
            while RUNNING and (time.time() - START_TIME) < MAX_RUNTIME:
                try:
                    # Случайная задержка для распределения нагрузки
                    await self.safe_sleep(random.uniform(1, 10))
                    
                    # Запрос заданий
                    await self.app.send_message(self.target_bot, "💎 Задания")
                    
                    # Ожидание ответа
                    await self.safe_sleep(random.uniform(10, 20))
                    
                    # Проверка ответов
                    has_tasks = False
                    async for msg in self.app.get_chat_history(self.target_bot, limit=5):
                        if not RUNNING or (time.time() - START_TIME) >= MAX_RUNTIME:
                            break
                            
                        if not msg.text:
                            continue
                            
                        msg_text = msg.text.lower()
                        
                        # Проверка блокировки
                        if any(kw in msg_text for kw in ["сожалению", "попробуйте позже", "ограничен"]):
                            logger.warning(f"[{self.session_name}] Обнаружена блокировка! Пауза 10 минут")
                            await self.safe_sleep(60)
                            continue
                            
                        # Обработка заданий
                        if "подпишитесь" in msg_text:
                            has_tasks = True
                            await self.process_task(msg)
                    
                    # Определение времени ожидания
                    wait_time = random.randint(5, 7) if not has_tasks else random.randint(30, 60)
                    logger.info(f"[{self.session_name}] Следующая проверка через {wait_time} сек.")
                    await self.safe_sleep(wait_time)
                    await self.app.send_message(self.target_bot, "💎 Задания")
                    
                    # Сброс счетчика ошибок после успешной итерации
                    self.error_count = max(0, self.error_count - 1)
                    
                except FloodWait as e:
                    wait_time = e.value + random.randint(5, 15)
                    logger.warning(f"[{self.session_name}] Ожидание FloodWait: {wait_time} сек.")
                    await self.safe_sleep(wait_time)
                except RPCError as e:
                    self.error_count += 1
                    logger.error(f"[{self.session_name}] RPCError: {e}. Ошибка #{self.error_count}")
                    
                    if self.error_count > self.max_errors:
                        logger.warning(f"[{self.session_name}] Слишком много ошибок! Пауза 1 час")
                        await self.safe_sleep(360)
                        self.error_count = 0
                    else:
                        await self.safe_sleep(60)
                except Exception as e:
                    self.error_count += 1
                    logger.error(f"[{self.session_name}] Неизвестная ошибка: {e}. Ошибка #{self.error_count}")
                    await self.safe_sleep(60)
                finally:
                    await self.close_http_session()  # Закрываем HTTP-сессию
            
            logger.info(f"[{self.session_name}] Работа аккаунта завершена")

async def account_supervisor(worker):
    """Контроль работы аккаунта с автоматическим перезапуском"""
    while RUNNING and (time.time() - START_TIME) < MAX_RUNTIME:
        try:
            await worker.main_loop()
        except Exception as e:
            logger.error(f"[{worker.session_name}] Критическая ошибка: {e}. Перезапуск через 60 сек.")
            await asyncio.sleep(60)
    
    logger.info(f"[{worker.session_name}] Супервизор завершил работу")

async def main():
    """Основная функция запуска"""
    global RUNNING
    
    # Пример данных аккаунтов (замените на реальные)
    accounts = [
        {"session": "account_4", "api_id": 24992059, "api_hash": "cc5be678c5ca65dab8487b45d89f2fee"}
        # Добавьте сюда остальные 174 аккаунта
    ]

    workers = []
    tasks = []
    
    # Создаем воркеры и задачи
    for acc in accounts:
        worker = AccountWorker(
            session_name=acc["session"],
            api_id=acc["api_id"],
            api_hash=acc["api_hash"]
        )
        workers.append(worker)
        task = asyncio.create_task(account_supervisor(worker))
        tasks.append(task)
        await asyncio.sleep(0.5)  # Интервал между запуском аккаунтов

    # Работаем 48 часов
    logger.info(f"Программа запущена. Работаем 48 часов.")
    await asyncio.sleep(MAX_RUNTIME)
    
    # Плавное завершение
    logger.info("Завершение работы...")
    RUNNING = False
    
    # Даем аккаунтам время на завершение
    await asyncio.sleep(30)
    
    # Отменяем все задачи
    for task in tasks:
        task.cancel()
    
    # Ожидаем завершения
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Программа успешно завершена")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
    finally:
        RUNNING = False
