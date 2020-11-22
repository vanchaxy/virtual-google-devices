import base64

from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from actions.authorization import AuthorizationPolicy
from actions.middlewares import setup_middlewares
from actions.routes import setup_routes
from actions.settings import POSTGRE_DNS, SECRET


async def db_engine(app):
    app["db_engine"] = create_async_engine(
        POSTGRE_DNS, echo=True,
    )
    async with app["db_engine"].connect() as conn:
        await conn.execute(select(1))
    try:
        yield app["db_engine"]
    finally:
        await app["db_engine"].dispose()


def setup_app():
    app = web.Application(middlewares=setup_middlewares())
    app.cleanup_ctx.append(db_engine)

    secret_key = base64.urlsafe_b64decode(SECRET)
    setup_session(app, EncryptedCookieStorage(secret_key))
    setup_security(
        app,
        SessionIdentityPolicy(),
        AuthorizationPolicy(app),
    )
    setup_routes(app)
    return app
