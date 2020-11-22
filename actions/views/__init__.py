from actions.views.actions import setup_actions_routes
from actions.views.auth import setup_auth_routes
from actions.views.device import setup_device_routes
from actions.views.user import setup_user_routes

__all__ = [
    "setup_actions_routes",
    "setup_user_routes",
    "setup_auth_routes",
    "setup_device_routes",
]
