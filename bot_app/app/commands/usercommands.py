from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from bot_app.app.keyboards.inline.main_inline import get_categories_boots, get_category_item_boots, get_categories_hats, get_category_item_hats, get_categories_clothes, get_category_item_clothes, get_categories_accessories, get_category_item_accessories as ikb


import bot_app.app.keyboards.reply.start_kb as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Добро пожаловать в магазин одежды', reply_markup=kb.main)


@router.message(F.text == 'Catalog')
async def catalog(message: Message):
    await message.answer('Выберите категорию товара', reply_markup=await ikb.categories())



