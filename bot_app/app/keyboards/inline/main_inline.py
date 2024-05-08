from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_app.app.database.requests.mainrequests import get_categories, get_category_item


async def categories():
    all_categories = await get_categories()# взяли все категории
    keyboard = InlineKeyboardBuilder()# делаем билдер
    for category in all_categories:# пошёл цикл по всем каториям
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='To main', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def items(category_id):
    all_items = get_category_item()
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='To main', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()