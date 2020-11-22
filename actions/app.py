from aiohttp import web

from actions.setup import setup_app

if __name__ == "__main__":
    app = setup_app()
    web.run_app(app)
