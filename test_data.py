import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from actions.db.tables import Base, Device, User
from actions.domain import DeviceType
from actions.domain.trait import TraitType
from actions.settings import POSTGRE_DNS

engine = create_async_engine(
    POSTGRE_DNS, echo=True,
)


async def create_all(en):
    async with en.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(en) as session:
        user = User(
            is_active=True,
            email="user@example.com",
            username="user",
        )
        user.set_password("password")

        device = Device(
            type=DeviceType.DOOR,
            traits=[TraitType.OpenClose],
            name='door',
            nicknames=[],
            attributes={},
            states={},
            user=user
        )
        session.add(user)
        session.add(device)

        await session.commit()


loop = asyncio.get_event_loop()
loop.run_until_complete(create_all(engine))
