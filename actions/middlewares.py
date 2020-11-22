from aiohttp import web


def setup_middlewares():
    return [
        web.normalize_path_middleware(
            append_slash=False,
            remove_slash=True,
        ),
    ]
