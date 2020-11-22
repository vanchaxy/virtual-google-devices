import uuid
from http import HTTPStatus

from aiohttp import web
from aiohttp_security import authorized_userid, forget, remember
from aiohttp_session import get_session
from sqlalchemy import not_, select

from actions.authorization import check_credentials
from actions.db import get_user_by_email
from actions.db.tables import Token, TokenType
from actions.helpers import provide_session
from actions.settings import CLIENT_ID, CLIENT_SECRET, GOOGLE_REDIRECT_URLS


@provide_session(autocommit=True)
async def authorization(session, request):
    userid = await authorized_userid(request)
    if userid is None:
        user_session = await get_session(request)
        user_session['redirect_after_login'] = str(request.url)  # TODO use ref url params
        return web.HTTPFound("/api/login")  # TODO redirect to front app login

    client_id = request.rel_url.query.get('client_id')
    redirect_uri = request.rel_url.query.get('redirect_uri')
    state = request.rel_url.query.get('state')

    if client_id != CLIENT_ID or redirect_uri not in GOOGLE_REDIRECT_URLS:
        return web.HTTPUnauthorized()

    user = await get_user_by_email(session, userid)
    token = Token(
        type=TokenType.authorization_code,
        code=uuid.uuid4().hex,
        user=user,
    )
    token.set_ttl(10 * 60)
    session.add(token)

    location = f"{redirect_uri}?code={token.code}&state={state}"
    return web.HTTPFound(location)


@provide_session(autocommit=True)
async def token_exchange(session, request):
    form = await request.post()
    grant_type = form.get('grant_type')
    client_id = form.get('client_id')
    client_secret = form.get('client_secret')
    if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
        return web.json_response(
            data={"error": "invalid_grant"},
            status=HTTPStatus.BAD_REQUEST,
        )
    if grant_type == 'authorization_code':
        return await process_authorization(session, form)
    if grant_type == 'refresh_token':
        return await process_refresh(session, form)


async def process_authorization(session, form):
    code = form.get('code')

    authorization_code = await session.execute(
        select(Token).where(
            (Token.type == TokenType.authorization_code)
            & (Token.code == code)
            & not_(Token.is_expired)
        )
    )
    authorization_code = authorization_code.scalars().first()
    if not authorization_code:
        return web.json_response(
            data={"error": "invalid_grant"},
            status=HTTPStatus.BAD_REQUEST,
        )

    access_token = Token(
        type=TokenType.access_token,
        code=uuid.uuid4().hex,
        user_id=authorization_code.user_id,
    )
    access_token_ttl = 60 * 60
    access_token.set_ttl(access_token_ttl)
    session.add(access_token)

    refresh_token = Token(
        type=TokenType.refresh_token,
        code=uuid.uuid4().hex,
        user_id=authorization_code.user_id,
    )
    session.add(refresh_token)

    return web.json_response(
        data={
            "token_type": "Bearer",
            "access_token": access_token.code,
            "refresh_token": refresh_token.code,
            "expires_in": access_token_ttl
        }
    )


async def process_refresh(session, form):
    token = form.get('refresh_token')

    refresh_token = await session.execute(
        select(Token).where(
            (Token.type == TokenType.refresh_token)
            & (Token.code == token)
        )
    )
    refresh_token = refresh_token.scalars().first()
    if not refresh_token:
        return web.json_response(
            data={"error": "invalid_grant"},
            status=HTTPStatus.BAD_REQUEST,
        )

    access_token = Token(
        type=TokenType.access_token,
        code=uuid.uuid4().hex,
        user_id=refresh_token.user_id,
    )
    access_token_ttl = 60 * 60
    access_token.set_ttl(access_token_ttl)
    session.add(access_token)

    return web.json_response(
        data={
            "token_type": "Bearer",
            "access_token": access_token.code,
            "expires_in": access_token_ttl
        }
    )


@provide_session
async def login(session, request):
    # TODO remove when front will be ready
    # login_data = await request.json()
    # email = login_data.get('email')
    # password = login_data.get('password')

    email = "user@example.com"
    password = "password"

    if not (email and password):
        return web.json_response(
            data={"success": False, "error": "no email or password"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if await check_credentials(session, email, password):
        user = await get_user_by_email(session, email)
        response_data = {
            "success": True,
            "data": user.as_dict(),
        }

        user_session = await get_session(request)
        redirect_after_login = user_session.pop('redirect_after_login', None)  # TODO move to front app
        if redirect_after_login:
            response_data["redirect_to"] = redirect_after_login
            response = web.json_response(
                data=response_data,
                status=HTTPStatus.FOUND,
                headers={'Location': redirect_after_login}
            )
        else:
            response = web.json_response(
                data=response_data,
            )

        await remember(request, response, email)
        return response

    return web.json_response(
        data={"success": False, "error": "wrong email or password"},
        status=HTTPStatus.UNAUTHORIZED,
    )


async def logout(request):
    userid = await authorized_userid(request)
    if userid is None:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )
    response = web.json_response(
        data={"success": True}
    )
    await forget(request, response)
    return response


def setup_auth_routes(router):
    router.add_get('/api/auth', authorization, name='oauth-auth')
    router.add_post('/api/token', token_exchange, name='oauth-token')
    router.add_get('/api/login', login, name='login')
    router.add_post('/api/logout', logout, name='logout')
