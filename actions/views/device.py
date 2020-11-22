from http import HTTPStatus

from aiohttp import web
from aiohttp_security import authorized_userid
from sqlalchemy import select

from actions.db import get_user_by_email
from actions.db.tables import Device, User
from actions.domain import DeviceType
from actions.domain.trait import TraitType
from actions.helpers import provide_session


@provide_session
async def list_devices(session, request):
    user_email = await authorized_userid(request)
    if not user_email:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )

    devices = await session.execute(
        select(Device).join(User).where((User.email == user_email) & User.is_active)
    )
    devices = devices.scalars().all()
    return web.json_response({
        "success": True,
        "data": [d.serialize() for d in devices]
    })


@provide_session(autocommit=True)
async def create_device(session, request):
    user_email = await authorized_userid(request)
    if not user_email:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )
    user = await get_user_by_email(session, user_email)

    create_data = await request.json()
    device = Device(
        type=DeviceType(create_data['type']),
        traits=[TraitType(tt) for tt in create_data['traits']],
        name=create_data['name'],
        nicknames=create_data.get('nicknames', list()),
        attributes=create_data.get('attributes', dict()),
        states=dict(),
        user=user,
    )
    session.add(device)

    return web.json_response({"success": True})


@provide_session
async def get_device(session, request):
    user_email = await authorized_userid(request)
    if not user_email:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )

    device_id = int(request.match_info["id"])
    device = await session.execute(
        select(Device).join(User).where(
            (Device.id == device_id) &
            (User.email == user_email) &
            User.is_active
        )
    )
    device = device.scalars().first()
    if not device:
        return web.json_response(
            data={
                "success": False,
                "error": "device not found",
            },
            status=HTTPStatus.NOT_FOUND,
        )

    return web.json_response({
        "success": True,
        "data": device.serialize(),
    })


@provide_session(autocommit=True)
async def edit_device(session, request):
    user_email = await authorized_userid(request)
    if not user_email:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )

    device_id = int(request.match_info["id"])
    device = await session.execute(
        select(Device).join(User).where(
            (Device.id == device_id) &
            (User.email == user_email) &
            User.is_active
        )
    )
    device = device.scalars().first()
    if not device:
        return web.json_response(
            data={
                "success": False,
                "error": "device not found",
            },
            status=HTTPStatus.NOT_FOUND,
        )

    edit_data = await request.json()

    if device_type := edit_data.pop("type", None):
        device.type = DeviceType(device_type)

    if traits := edit_data.pop("traits", None):
        device.traits = [TraitType(tt) for tt in traits]

    for attr, value in edit_data.items():
        setattr(device, attr, value)

    return web.json_response({"success": True})


@provide_session(autocommit=True)
async def delete_device(session, request):
    user_email = await authorized_userid(request)
    if not user_email:
        return web.json_response(
            data={"success": False, "error": "not logged in"},
            status=HTTPStatus.UNAUTHORIZED,
        )

    device_id = int(request.match_info["id"])
    device = await session.execute(
        select(Device).join(User).where(
            (Device.id == device_id) &
            (User.email == user_email) &
            User.is_active
        )
    )
    device = device.scalars().first()
    if not device:
        return web.json_response(
            data={
                "success": False,
                "error": "device not found",
            },
            status=HTTPStatus.NOT_FOUND,
        )

    session.delete(device)
    return web.json_response({"success": True})


async def get_device_types(request):
    return web.json_response({
        "success": True,
        "data": [dt.value for dt in DeviceType],
    })


async def get_trait_types(request):
    return web.json_response({
        "success": True,
        "data": [tt.value for tt in TraitType],
    })


def setup_device_routes(router):
    router.add_get('/api/devices', list_devices, name='list-devices')
    router.add_post(r'/api/devices', create_device, name='create-device')

    router.add_get(r'/api/devices/{id:\d+}', get_device, name='get-device')
    router.add_patch(r'/api/devices/{id:\d+}', edit_device, name='edit-device')
    router.add_delete(r'/api/devices/{id:\d+}', delete_device, name='delete-device')

    router.add_get('/api/device-types', get_device_types, name='device-types')
    router.add_get('/api/trait-types', get_trait_types, name='trait-types')
