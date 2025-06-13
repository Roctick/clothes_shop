from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import logging
import os
import shutil
from jobseo_handler import AccountManager
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

# Состояния пользователя
class UserState(StatesGroup):
    WAITING_LOGIN = State()
    WAITING_PHOTO = State()

# Кнопки
def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Получить задание", callback_data="get_task")
    builder.button(text="📊 Статистика", callback_data="stats")
    builder.adjust(1)
    return builder.as_markup()

def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить задание")
    return builder.as_markup(resize_keyboard=True)

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
async def process_callback(callback: types.CallbackQuery, state: FSMContext):
    await process_task(callback.message, state)
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

async def process_task(message: types.Message, state: FSMContext):
    """Обработка получения нового задания"""
    try:
        # Проверяем время - работаем только с 6 утра
        now = datetime.datetime.now().time()
        if now.hour < 6:
            target = datetime.time(6, 0)
            now_datetime = datetime.datetime.now()
            target_datetime = datetime.datetime.combine(now_datetime.date(), target)
            if now_datetime > target_datetime:
                target_datetime += datetime.timedelta(days=1)
                
            wait_seconds = (target_datetime - now_datetime).total_seconds()
            wait_hours = int(wait_seconds // 3600)
            wait_minutes = int((wait_seconds % 3600) // 60)
            
            await message.answer(
                f"⏳ Бот начнет работу в 6 утра. До начала работы осталось: "
                f"{wait_hours} часов {wait_minutes} минут."
            )
            return

        # Проверяем наличие данных в очереди
        if manager.data_queue.empty():
            await message.answer("⏳ Нет доступных заданий. Попробуйте позже.")
            return

        # Получаем данные из очереди через менеджер
        data = await manager.get_parsed_data()
        logger.info(f"Получены данные: {data}")
        
        # Сохраняем данные задания в состоянии
        await state.update_data(
            account=data['account'],
            address=data['address'],
            direction=data['direction'],
            review=data['review']
        )
        
        # Отправляем адрес и отзыв отдельными сообщениями
        await message.answer(f"{data['address']}")
        await message.answer(f"\n\n{data['review']}")
        
        # Запрашиваем логин
        await message.answer(
            "🔑 Пожалуйста, введите логин аккаунта для этого задания:",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(UserState.WAITING_LOGIN)
        
    except Exception as e:
        error_msg = f"⚠️ Ошибка при получении задания: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await message.answer(error_msg)

@dp.message(UserState.WAITING_LOGIN)
async def process_login(message: types.Message, state: FSMContext):
    """Обработка полученного логина"""
    login = message.text.strip()
    if login.lower() == "❌ отменить задание":
        await state.clear()
        await message.answer("❌ Задание отменено.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    await state.update_data(login=login)
    await message.answer(
        "✅ Логин сохранен! Теперь отправьте фото отзыва:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserState.WAITING_PHOTO)

@dp.message(UserState.WAITING_PHOTO, F.photo)
async def process_photo(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка полученного фото"""
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        account_name = data['account']
        login = data['login']
        
        # Скачиваем фото
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Создаем папку для фото, если нет
        os.makedirs("photos", exist_ok=True)
        local_path = f"photos/{file_id}.jpg"
        await bot.download_file(file_path, destination=local_path)
        
        # Отправляем отзыв и фото в @jobseo_bot через AccountManager
        success = await manager.send_review_with_photo(
            account_name, 
            data['review'],
            login,
            local_path
        )
        
        if success:
            await message.answer(
                "✅ Отзыв и фото успешно отправлены в систему!",
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.clear()
            await message.answer('/start')

        else:
            await message.answer(
                "❌ Не удалось отправить отзыв. Попробуйте снова.",
                reply_markup=types.ReplyKeyboardRemove()
            )
        
        # Завершаем состояние
        await state.clear()
            
    except Exception as e:
        error_msg = f"⚠️ Ошибка обработки фото: {str(e)}"
        logger.error(error_msg)
        await message.answer(error_msg)

@dp.message(UserState.WAITING_PHOTO)
async def wrong_photo_format(message: types.Message):
    """Обработка неправильного формата фото"""
    await message.answer("⚠️ Пожалуйста, отправьте фото отзыва.")

@dp.message(F.text == "❌ Отменить задание")
async def cancel_task(message: types.Message, state: FSMContext):
    """Отмена текущего задания"""
    await state.clear()
    await message.answer(
        "❌ Задание отменено.", 
        reply_markup=types.ReplyKeyboardRemove()
    )

async def cleanup_photos():
    """Очистка старых фото"""
    while True:
        await asyncio.sleep(86400)  # Каждый день
        try:
            shutil.rmtree("photos", ignore_errors=True)
            os.makedirs("photos", exist_ok=True)
            logger.info("Папка с фото очищена")
        except Exception as e:
            logger.error(f"Ошибка очистки фото: {str(e)}")

async def main():
    # Запускаем фоновые задачи
    await start_accounts()
    asyncio.create_task(cleanup_photos())
    logger.info("Фоновые задачи запущены")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Создаем папки для сессий и фото
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("photos", exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}", exc_info=True)