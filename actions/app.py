from aiohttp import web

from actions.settings import SERVER_PORT
from actions.setup import setup_app

if __name__ == "__main__":
    app = setup_app()
    web.run_app(app, port=SERVER_PORT)
