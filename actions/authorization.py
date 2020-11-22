from aiohttp_security.abc import AbstractAuthorizationPolicy
from sqlalchemy.ext.asyncio import AsyncSession

from actions.db import check_if_user_exist, get_user_by_email


class AuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, app):
        self.app = app

    @property
    def engine(self):
        return self.app["db_engine"]

    async def authorized_userid(self, identity):
        async with AsyncSession(self.engine) as session:
            user = await check_if_user_exist(session, identity)
            if user:
                return identity

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return True


async def check_credentials(session, email, password):
    user = await get_user_by_email(session, email)
    if user:
        return user.check_password(password)
