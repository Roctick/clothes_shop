from aiogram.fsm.state import State, StatesGroup\



class Register(StatesGroup):
    name = State()
    number = State()
