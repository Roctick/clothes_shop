import asyncio

from aiogram import Bot, Dispatcher
from bot_app.app.commands.usercommands import router

from bot_app.app.database.accessories_database.models import async_main1
from bot_app.app.database.boots_database.models import async_main2
from bot_app.app.database.clothes_database.models import async_main3
from bot_app.app.database.hats_database.models import async_main4
from bot_app.app.database.user_database.models import async_main5


async def main():
    await async_main1()
    await async_main2()
    await async_main3()
    await async_main4()
    await async_main5()
    bot = Bot(
        token='7128742085:AAFiS_mqP2QwJiI_TO6k-JdOSyJSGtqVX7w'
    )
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')



