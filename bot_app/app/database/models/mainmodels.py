from sqlalchemy import BigInteger, String, ForeignKey #импортируем типы данных которые будут в БД
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column #
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine # тк фреймворк асинхронный БД тоже ассинхронная

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')# создвём БД

async_session = async_sessionmaker(engine)#создвние сессии т.е запуск БД и создание колонок если их нет


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'# название таблицы

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    number = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(100))


class MainCategory(Base):
    __tablename__ = 'main_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class BootsCategory(Base):
    __tablename__ = 'boots_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class ClothesCategory(Base):
    __tablename__ = 'clothes_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class HatsCategory(Base):
    __tablename__ = 'had_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class AccessoriesCategory(Base):
    __tablename__ = 'accessories_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class BootsItem(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))# String(150) БД  требует ограничений
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[int] = mapped_column()
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    # Чтобы обратиться к вещи нам надо знать её категорию
    # Обращаемся мы к ней с помощью последней строчки


class HatsItem(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))# String(150) БД  требует ограничений
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[int] = mapped_column()
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))


class ClothesItem(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))# String(150) БД  требует ограничений
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[int] = mapped_column()
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))


class AccessoriesItem(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))# String(150) БД  требует ограничений
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[int] = mapped_column()
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
# ЧТО МЫ СДЕЛАЛИ
# мы создали БД и вызвали её асинхронно
# затем мы обьявили таблицы в той самой БД