from bot_app.app.database.user_database.models import async_session
from bot_app.app.database.user_database.models import User
from sqlalchemy import select

#импорт БД  и модуля select для взятия значений внутри


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()