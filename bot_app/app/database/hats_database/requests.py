from bot_app.app.database.hats_database.models import async_session
from bot_app.app.database.hats_database.models import Category, Item
from sqlalchemy import select


async def get_categories_hats():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_item_hats(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_item_hats(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))