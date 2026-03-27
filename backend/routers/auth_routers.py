

from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from backend.utils.user_parser import get_allowed_users
from backend.utils.jwt_handler import create_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login")
def login(data: dict):
    users = get_allowed_users()

    email = data.get("email")
    password = data.get("password")

    if email not in users:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = users[email]

    if not pwd_context.verify(password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_token({"email": email})

    return {
        "access_token": token,
        "email": email
    }