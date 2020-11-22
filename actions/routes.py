from actions.views import (setup_actions_routes, setup_auth_routes,
                           setup_device_routes, setup_user_routes)


def setup_routes(app):
    setup_actions_routes(app.router)
    setup_auth_routes(app.router)
    setup_device_routes(app.router)
    setup_user_routes(app.router)
