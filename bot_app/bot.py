import asyncio

from aiogram import Bot, Dispatcher
from bot_app.app.commands.usercommands import router

from bot_app.app.database.models.mainmodels import async_main


async def main():
    await async_main()
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



