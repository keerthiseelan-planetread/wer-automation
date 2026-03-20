import bcrypt
from app.config import Config


def authenticate_user(username: str, password: str) -> str | None:
    allowed_users = Config.get_allowed_users()
    hashed = allowed_users.get(username)
    if not hashed:
        return None
    if bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8")):
        return username
    return None