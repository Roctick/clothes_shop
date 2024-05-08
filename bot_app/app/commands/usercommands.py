from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from bot_app.app.keyboards.inline.main_inline import categories, get_categories, get_category_item as ikb


import bot_app.app.keyboards.reply.start_kb as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Добро пожаловать в магазин одежды', reply_markup=kb.main)


@router.message(F.text == 'Catalog')
async def catalog(message: Message):
    await message.answer('Выберите категорию товара', reply_markup=await ikb.categories())



