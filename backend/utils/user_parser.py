from app.config import Config

def get_allowed_users():
    users_raw = Config.ALLOWED_USERS.split(",")

    users = {}
    for user in users_raw:
        email, password = user.split(":")
        users[email] = password

    return users