from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import logging
import os
from jobseo_handler import AccountManager  # Измененный импорт
import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "7624493586:AAEdaydxfLVwKt54A3tNcE3wFQFgQ74j3Yw"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальный экземпляр AccountManager
manager = AccountManager()

# Кнопки
def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Получить задание", callback_data="get_task")
    builder.button(text="📊 Статистика", callback_data="stats")
    builder.adjust(1)  # Расположение кнопок в один столбец
    return builder.as_markup()

# Функция для запуска аккаунтов в фоне
async def start_accounts():
    """Фоновая задача для запуска системы обработки аккаунтов"""
    await manager.init_accounts()
    asyncio.create_task(manager.start_work())

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в систему управления заданиями!\n"
        "Используйте кнопки ниже для управления:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(lambda c: c.data == "get_task")
async def process_callback(callback: types.CallbackQuery):
    await process_task(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "stats")
async def show_stats(callback: types.CallbackQuery):
    try:
        active_accounts = len(manager.account_clients)
        queue_size = manager.data_queue.qsize()
        processed_today = manager.processed_today
        
        stats_message = (
            f"📊 Статистика системы:\n"
            f"Активных аккаунтов: {active_accounts}\n"
            f"Заданий в очереди: {queue_size}\n"
            f"Обработано сегодня: {processed_today}"
        )
        
        await callback.message.answer(stats_message)
    except Exception as e:
        logger.error(f"Ошибка статистики: {str(e)}")
        await callback.message.answer(f"⚠️ Ошибка получения статистики: {str(e)}")
    
    await callback.answer()

async def process_task(message: types.Message):
    """Обработка получения нового задания"""
    try:
        # Проверяем наличие данных в очереди
        if manager.data_queue.empty():
            await message.answer("⏳ Нет доступных заданий. Попробуйте позже.")
            return

        # Получаем данные из очереди через менеджер
        data = await manager.get_parsed_data()
        logger.info(f"Получены данные: {data}")
        
        # Формируем ответ
        response = (
            f"🎯 Новое задание!\n\n"
            f"🔎 Аккаунт: {data['account']}\n"
            f"📍 Адрес: {data['address']}\n"
            f"🏷 Направление: {data['direction']}\n\n"
            f"✏️ Готовый отзыв:\n\n{data['review']}"
        )
        
        # Отправляем ответ пользователю
        await message.answer(response)
        
    except Exception as e:
        error_msg = f"⚠️ Ошибка при получении задания: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await message.answer(error_msg)

async def main():
    # Запускаем фоновые задачи
    await start_accounts()
    logger.info("Фоновые задачи запущены")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Создаем папку для сессий
    os.makedirs("sessions", exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
