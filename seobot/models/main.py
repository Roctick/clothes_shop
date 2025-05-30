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
from jobseo_handler import AccountManager  # Импортируем класс
import datetime


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "7395130406:AAHnvZRL1kMqTHpGRQ0SN0Ork02LUtCA6j8"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальный экземпляр AccountManager
manager = AccountManager()

# Состояния пользователя
class UserState(StatesGroup):
    WAITING_NAME = State()
    WAITING_PHOTO = State()

# Кнопки
def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Получить задание", callback_data="get_task")
    builder.button(text="📊 Статистика", callback_data="stats")
    return builder.as_markup()

def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить задание")
    return builder.as_markup(resize_keyboard=True)

# Функция для запуска аккаунтов в фоне
async def start_accounts():
    """Фоновая задача для запуска системы обработки аккаунтов"""
    await manager.init_accounts()
    await manager.start_work()  # Используем новый метод запуска

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
    active_accounts = len(manager.clients)
    tasks_in_queue = sum(q.qsize() for q in manager.task_queues.values())
    
    await callback.message.answer(
        f"📊 Статистика системы:\n"
        f"Активных аккаунтов: {active_accounts}\n"
        f"Заданий в обработке: {tasks_in_queue}\n"
        f"Пользователей с заданиями: {len(UserState)}"
    )
    await callback.answer()

async def process_task(message: types.Message):
    """Обработка получения нового задания"""
    try:
        # Проверяем время - работаем только с 6 утра
        now = datetime.datetime.now().time()
        if now.hour < 6:
            # Рассчитываем время до 6 утра
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

        # Получаем данные из очереди
        try:
            data = await asyncio.wait_for(manager.get_parsed_data(), timeout=30.0)
            logger.info(f"Получены данные: {data}")
        except asyncio.TimeoutError:
            await message.answer("⏳ Нет доступных заданий. Попробуйте позже.")
            return
        
        # Формируем ответ с готовым отзывом
        response = (
            f"🎯 Новое задание!\n\n"
            f"🔎 Аккаунт: {data['account']}\n"
            f"📍 Адрес: {data['address']}\n"
            f"🏷 Направление: {data['direction']}\n\n"
            f"✏️ Готовый отзыв:\n\n{data['review']}\n\n"
            f"Отзыв будет отправлен автоматически."
        )
        
        # Отправляем данные в @jobseo_bot
        success = await manager.send_review(
            data['account'], 
            data['review']
        )
        
        if success:
            await message.answer(response + "\n\n✅ Отзыв успешно отправлен!")
        else:
            await message.answer(response + "\n\n❌ Не удалось отправить отзыв. Попробуйте снова.")
        
    except Exception as e:
        error_msg = f"⚠️ Ошибка: {str(e)}"
        logger.error(error_msg)
        await message.answer(error_msg)

@dp.message(UserState.WAITING_NAME)
async def process_name(message: types.Message, state: FSMContext):
    """Обработка полученного имени"""
    # Сохраняем имя в состоянии
    await state.update_data(user_name=message.text)
    
    # Переводим в состояние ожидания фото
    await state.set_state(UserState.WAITING_PHOTO)
    
    await message.answer(
        "✅ Имя сохранено! Теперь отправьте фото отзыва:",
        reply_markup=get_cancel_keyboard()
    )

@dp.message(UserState.WAITING_PHOTO, F.photo)
async def process_photo(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка полученного фото"""
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        account_name = data['account']
        user_name = data['user_name']
        address = data['address']
        
        # Скачиваем фото
        photo = message.photo[-1]  # Берем самое большое фото
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Создаем папку для фото, если нет
        os.makedirs("photos", exist_ok=True)
        local_path = f"photos/{file_id}.jpg"
        await bot.download_file(file_path, destination=local_path)
        
        # Отправляем отзыв через accounts_manager
        success = await manager.send_review(account_name, user_name, local_path)
        
        if success:
            # Формируем ответ
            response = (
                f"✅ Отзыв отправлен в систему!\n\n"
                f"🔎 Аккаунт: {account_name}\n"
                f"👤 Имя: {user_name}\n"
                f"📍 Адрес: {address}\n"
            )
            await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer("❌ Не удалось отправить отзыв. Попробуйте снова.")
        
        # Завершаем состояние
        await state.clear()
            
        logger.info(f"Задание завершено для пользователя {message.from_user.id}")
        
    except Exception as e:
        error_msg = f"⚠️ Ошибка обработки фото: {str(e)}"
        logger.error(error_msg)
        await message.answer(error_msg)

@dp.message(UserState.WAITING_PHOTO)
async def wrong_photo_format(message: types.Message):
    """Обработка неправильного формата фото"""
    await message.answer("⚠️ Пожалуйста, отправьте фото отзыва. Используйте кнопку '📷 Фото' в Telegram.")

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
            shutil.rmtree("photos")
            os.makedirs("photos", exist_ok=True)
            logger.info("Папка с фото очищена")
        except Exception as e:
            logger.error(f"Ошибка очистки фото: {str(e)}")

async def main():
    # Запускаем фоновые задачи
    asyncio.create_task(start_accounts())
    asyncio.create_task(cleanup_photos())
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())