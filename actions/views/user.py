from http import HTTPStatus

from aiohttp import web
from aiohttp_security import authorized_userid

from actions.db import check_if_user_exist, get_user_by_email
from actions.db.tables import User
from actions.helpers import is_valid_email, provide_session


@provide_session
async def get_user(session, request):
    email = await authorized_userid(request)
    if not email:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )
    user = await get_user_by_email(session, email)
    return web.json_response({
        "success": True,
        "data": user.as_dict(),
    })


@provide_session(autocommit=True)
async def create_user(session, request):
    register_data = await request.json()
    email = register_data.get('email')
    if not email or not is_valid_email(email):
        return web.json_response(
            data={"success": False, "error": "invalid email"},
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if await check_if_user_exist(session, email):
        return web.json_response(
            data={"success": False, "error": "email already exist"},
            status=HTTPStatus.CONFLICT,
        )
    username = register_data.get('username')
    password = register_data.get('password')

    new_user = User(
        is_active=True,
        email=email,
        username=username,
    )
    new_user.set_password(password)
    session.add(new_user)

    return web.json_response({"success": True})


@provide_session(autocommit=True)
async def edit_user(session, request):
    userid = await authorized_userid(request)
    if not userid:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )
    user = await get_user_by_email(session, userid)

    edit_data = await request.json()
    email = edit_data.get('email')
    if email:
        if not is_valid_email(email):
            return web.json_response(
                data={"success": False, "error": "invalid email"},
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        user.email = email

    username = edit_data.get('username')
    if username:
        user.username = username

    password = edit_data.get('password')
    if password:
        user.set_password(password)

    return web.json_response({"success": True})


def setup_user_routes(router):
    router.add_get('/api/user', get_user, name='get-user')
    router.add_post('/api/user', create_user, name='create-user')
    router.add_patch('/api/user', edit_user, name='edit-user')
