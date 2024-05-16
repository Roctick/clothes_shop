from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_app.app.database.accessories_database.requests import get_categories_accessories, get_category_item_accessories
from bot_app.app.database.boots_database.requests import get_categories_boots, get_category_item_boots
from bot_app.app.database.clothes_database.requests import get_categories_clothes, get_category_item_clothes
from bot_app.app.database.hats_database.requests import get_categories_hats, get_category_item_hats


async def categories():
    all_categories = await get_categories_accessories(), get_categories_clothes(), get_categories_hats(), get_categories_boots() # взяли все категории
    keyboard = InlineKeyboardBuilder()# делаем билдер
    for category in all_categories:# пошёл цикл по всем каториям
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='To main', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def items(category_id):
    all_items = get_category_item_accessories(), get_category_item_hats(), get_category_item_clothes(), get_category_item_boots()
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='To main', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()