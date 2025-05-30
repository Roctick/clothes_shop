from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import logging
import time 

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

api_id = 25709715
api_hash = "71342afcaef835c71a09a659b5561b95"
target_bot = "@StarsovEarnBot"

app = Client("my_account", api_id=api_id, api_hash=api_hash)

async def solve_captcha(message: Message):
    """Решает капчу с изображением"""
    try:
        if "изображен" in message.text.lower() and message.reply_markup:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if "🍎" in button.text or "яблоко" in button.text.lower():
                        await message.click(button.text)
                        logger.info("Капча решена!")
                        return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при решении капчи: {e}")
        return False

async def process_message(message: Message):
    """Обрабатывает новые сообщения от бота"""
    if "Подпишитесь" in message.text:
        logger.info("Найдено задание: Подписка")
        if message.reply_markup:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if "Подписаться" in button.text:
                        await message.click(button.text)
                        logger.info(f"Выполнено: {button.text}")
                        await asyncio.sleep(15)
        return True

    elif "изображен" in message.text.lower():
        logger.info("Обнаружена капча")
        return await solve_captcha(message)
    else:
        return False

async def process_subscriptions(message: Message):
    """Обрабатывает задания по подпискам: переход → подписка → подтверждение"""
    try:
        if not message.reply_markup:
            return False

        # Шаг 1: Найти кнопку "🔎 Перейти"
        join_button = None
        for row in message.reply_markup.inline_keyboard:
            for button in row:
                if "перейти" in button.text.lower() and "🔎" in button.text:
                    join_button = button
                    break

        if not join_button or not hasattr(join_button, "url"):
            logger.warning("Кнопка перехода не найдена или не содержит URL")
            return False

        url = join_button.url
        logger.info(f"Попытка обработать ссылку: {url}")

        # Обработка ссылок
        if "t.me/" in url:
            clean_url = url.split("?")[0]
            target = clean_url.split("/")[-1]

            # Если это бот с параметром start= (например, t.me/StarsEarnRuBot?start=...)
            if "start=" in url:
                # Извлекаем параметр start
                start_param = url.split("start=")[-1]
                # Запускаем бота с параметром
                await app.send_message(target, f"/start {start_param}")
                logger.info(f"Бот {target} запущен с параметром: {start_param}")
            else:
                # Для каналов и чатов
                try:
                    await app.join_chat(target)
                    logger.info(f"Успешно вступили в: {target}")
                except Exception as e:
                    logger.error(f"Ошибка вступления: {str(e)[:50]}")
                    return False

        await asyncio.sleep(5)

        # Шаг 2: Подтверждение подписки
        confirm_button = None
        for row in message.reply_markup.inline_keyboard:
            for button in row:
                if any(kw in button.text.lower() for kw in ["подтвердить", "confirm"]):
                    confirm_button = button
                    break

        if confirm_button:
            await message.click(confirm_button.text)
            logger.info("Подтверждение отправлено")
            await asyncio.sleep(10)
            return True

        return False

    except Exception as e:
        logger.error(f"Ошибка в process_subscriptions: {str(e)}")
        return False

@app.on_message(filters.bot & filters.private)
async def handle_bot_messages(client, message: Message):
    """Обрабатывает все сообщения от целевого бота"""
    if message.from_user.username == target_bot.replace("@", ""):
        await process_message(message)


async def main_loop():
    """Основной цикл с улучшенным детектированием активности"""
    async with app:
        while True:
            try:
                logger.info("--- Новый цикл запущен ---")
                
                # Шаг 1: Отправка команды
                await app.send_message(target_bot, "💎 Задания")
                logger.info("Команда отправлена")
                
                # Инициализация времени и состояния
                start_time = time.time()
                activity_detected = False
                block_detected = False
                
                # Мониторинг сообщений
                while not block_detected:
                    activity_detected = False
                    
                    # Получаем сообщения за последние 2 минуты
                    async for message in app.get_chat_history(target_bot, limit=30):
                        msg_time = message.date.timestamp()
                        
                        # Фильтр по времени (последние 2 минуты)
                        if msg_time < start_time - 120:  # Учитываем задержку отправки
                            continue
                            
                        text = (message.text or "").lower()
                        logger.debug(f"Получено сообщение: {text}")  # Добавлено для отладки
                        
                        # Сценарий 1: Блокировка
                        if any(kw in text for kw in ["сожалению", "попробуйте позже"]):
                            logger.warning("Обнаружена блокировка! Перезапуск через 10 минут")
                            block_detected = True
                            break
                            
                        # Сценарий 2: Капча
                        elif any(kw in text for kw in ["изображен", "выберите"]):
                            logger.info("Обнаружена капча")
                            await solve_captcha(message)
                            activity_detected = True
                            
                        # Сценарий 3: Задания
                        elif any(kw in text for kw in ["подпишитесь", "подпишись", "задание"]):
                            logger.info("Обработка заданий...")
                            await process_subscriptions(message)
                            activity_detected = True
                            
                        # Любое новое сообщение = активность
                        else:
                            activity_detected = True  # Любое сообщение учитывается
                    
                    # Перезапуск при блокировке
                    if block_detected:
                        await asyncio.sleep(600)
                        break
                        
                    # Перезапуск при отсутствии активности
                    if not activity_detected:
                        logger.warning("Активность не обнаружена. Перезапуск через 10 минут")
                        await asyncio.sleep(600)
                        break
                        
                    await asyncio.sleep(10)  # Уменьшен интервал проверки
                
            except Exception as e:
                logger.error(f"ОШИБКА: {e}. Перезапуск через 10 минут")
                await asyncio.sleep(600)

if __name__ == "__main__":
    app.run(main_loop())