from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='Catalog'),
        KeyboardButton(text='Bin')
    ],
    [
        KeyboardButton(text='Profile'),
        KeyboardButton(text='Another')
    ],
    [
        KeyboardButton(text='About us')
    ]], resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Select an action...'
)