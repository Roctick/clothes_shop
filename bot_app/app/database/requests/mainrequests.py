from bot_app.app.database.models.mainmodels import async_session
from bot_app.app.database.models.mainmodels import User, Item, MainCategory, ClothesCategory, HatsCategory, BootsCategory, AccessoriesCategory
from sqlalchemy import select

#импорт БД  и модуля select для взятия значений внутри


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_main_categories():
    async with async_session() as session:
        return await session.scalars(select(MainCategory))


async def get_main_category_category(main_category_id):
    async with async_session() as session:
        return await session.scalars(select(Category).where(MainCategory.category == main_category_id))

async def get_categories(maincategory_id):
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_item(item_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.id == item_id))





