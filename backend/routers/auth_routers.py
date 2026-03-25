# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm

# from backend.schemas.auth import Token
# from backend.services.auth import authenticate_user
# from backend.core.security import create_access_token

# router = APIRouter()


# @router.post("/login", response_model=Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
#     access_token = create_access_token(subject=user)
#     return {"access_token": access_token, "token_type": "bearer"}


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