import os

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
PROJECT_ID = os.environ["PROJECT_ID"]

SECRET = os.environ["SECRET"]

POSTGRE_DNS = os.environ["POSTGRE_DNS"]

GOOGLE_REDIRECT_URLS = [
    f"https://oauth-redirect.googleusercontent.com/r/{PROJECT_ID}",
    f"https://oauth-redirect-sandbox.googleusercontent.com/r/{PROJECT_ID}"
]

SERVER_PORT = int(os.environ.get("SERVER_PORT", 8080))
