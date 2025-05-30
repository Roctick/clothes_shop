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

# Конфигурация
api_id = 24992059
api_hash = "cc5be678c5ca65dab8487b45d89f2fee"
target_bot = "@jobseo_bot"

# Инициализация клиента с использованием сессии
app = Client("account_4", api_id=api_id, api_hash=api_hash)

async def send_initial_command():
    """Отправляет стартовую команду боту"""
    await app.send_message(target_bot, "Приступить к заданию ✍️")
    logger.info("Стартовая команда отправлена")

async def handle_task_response(message: Message):
    """Обрабатывает ответы от бота"""
    text = message.text or ""
    
    # Если бот прислал задание с выбором города
    if "выберите город" in text.lower():
        await message.reply("Тамбов")
        logger.info("Город 'Тамбов' отправлен")
    
    # Если бот запросил выбор платформы
    elif "выберите платформу" in text.lower():
        await message.reply("2Gis")
        logger.info("Платформа '2Gis' отправлена")
    
    # Если задание подтверждено
    elif "задание принято" in text.lower():
        logger.success("Задание выполнено!")

# Хэндлер для всех сообщений от целевого бота
@app.on_message(filters.bot & filters.user(target_bot))
async def on_bot_message(client: Client, message: Message):
    await handle_task_response(message)

async def main():
    """Основной цикл работы"""
    async with app:
        # Отправляем начальную команду
        await send_initial_command()
        
        # Бесконечный цикл для поддержания сессии
        while True:
            await asyncio.sleep(10)

if __name__ == "__main__":
    # Запуск с предупреждением о необходимости сессии
    print("Убедитесь, что сессия 'my_account.session' авторизована!")
    asyncio.run(main())