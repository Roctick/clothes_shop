from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

import bot_app.app.keyboards.reply.start_kb as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Добро пожаловать в магазин одежды', reply_markup=kb.main)
