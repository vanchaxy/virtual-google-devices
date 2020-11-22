import logging
from enum import Enum

from aiohttp import web
from sqlalchemy import select

from actions.db.tables import Device, Token, TokenType, User
from actions.helpers import provide_session


class Intent(Enum):
    SYNC = "action.devices.SYNC"
    QUERY = "action.devices.QUERY"
    EXECUTE = "action.devices.EXECUTE"
    DISCONNECT = "action.devices.DISCONNECT"


@provide_session(autocommit=True)
async def fulfillment(session, request):
    auth_header = request.headers["Authorization"]
    access_token = auth_header.split()[1]

    user = await session.execute(
        select(User).join(Token).where(
            (Token.type == TokenType.access_token)
            & (Token.code == access_token)
            & User.is_active
        )
    )
    user = user.scalars().first()
    if not user:
        raise web.HTTPUnauthorized()

    intent_data = await request.json()
    inputs = intent_data["inputs"]
    if len(inputs) > 1:
        logging.warning("More than 1 intent is not supported")
    intent = inputs[0]["intent"]

    if intent == Intent.DISCONNECT.value:
        return web.json_response({})

    payload = await INTENT_TO_PROCESSOR[intent](session, user, inputs[0])
    return web.json_response({
        "requestId": intent_data["requestId"],
        "payload": payload,
    })


async def process_sync_intent(session, user, input_data):
    devices = await session.execute(
        select(Device).where(Device.user == user)
    )
    devices = devices.scalars()
    return {
        "agentUserId": user.id,
        "devices": [
            device.serialize_info() for device in devices
        ],
    }


async def process_query_intent(session, user, input_data):
    ids = [int(d["id"]) for d in input_data["payload"]["devices"]]
    devices = await session.execute(
        select(Device).where(Device.user == user & Device.id.in_(ids))
    )
    devices = devices.scalars()
    return {
        "devices": {
            device.id: device.serialize_status() for device in devices
        },
    }


async def process_execute_intent(session, user, input_data):
    success = []
    error = []
    for command in input_data["payload"]["commands"]:
        ids = [int(d["id"]) for d in command["devices"]]
        devices = await session.execute(
            select(Device).where((Device.user == user) & Device.id.in_(ids))
        )
        devices = devices.scalars().all()
        for device in devices:
            try:
                for execution in command["execution"]:
                    device.execute_command(**execution)
            except BaseException:
                error.append(device.id)
            else:
                success.append(device.id)
    return {
        "commands": [
            {
                "ids": [i for i in success],
                "status": "SUCCESS",
                "states": {
                    "on": True,
                    "online": True,
                },
            },
            {
                "ids": [i for i in error],
                "status": "ERROR",
            },
        ],
    }


INTENT_TO_PROCESSOR = {
    Intent.SYNC.value: process_sync_intent,
    Intent.QUERY.value: process_query_intent,
    Intent.EXECUTE.value: process_execute_intent,
}


def setup_actions_routes(router):
    router.add_post('/api/fulfillment', fulfillment, name='fulfillment')
