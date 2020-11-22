from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession


def provide_session(_func=None, *, autocommit=False):
    def decorator_provider(fn):

        @wraps(fn)
        async def wrapped(*args, **kwargs):
            request = args[-1]
            db_engine = request.app["db_engine"]
            async with AsyncSession(db_engine) as session:
                response = await fn(session, *args, **kwargs)
                if autocommit:
                    await session.commit()
                return response

        return wrapped

    if _func is None:
        return decorator_provider
    else:
        return decorator_provider(_func)
