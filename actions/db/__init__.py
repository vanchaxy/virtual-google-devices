from sqlalchemy import select
from sqlalchemy.sql.functions import count

from actions.db.tables import User

__all__ = ["check_if_user_exist", "get_user_by_email", ]


async def check_if_user_exist(session, email):
    user = await session.execute(
        select(count(User.id)).where(User.email == email and User.is_active)
    )
    return bool(user.scalars().first())


async def get_user_by_email(session, email):
    user = await session.execute(
        select(User).where((User.email == email) & User.is_active)
    )
    return user.scalars().first()
