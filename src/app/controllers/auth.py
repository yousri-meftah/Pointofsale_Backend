from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.employee import Employee as UserModel
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.enums import AccountStatus
from app.services.token import verify_password
from core.config import settings
from app.services.token import (
    create_access_token,
    create_refresh_token,
    get_token_payload,
)
from app.schemas.auth import TokenResponse
from app.utils import hash_password
from app.enums import AccountStatus as userStatus
from core.config import settings


async def get_token(data: OAuth2PasswordRequestForm, db: Session):

    user = db.query(UserModel).filter(UserModel.email == data.username).first()

    if not user :
        raise HTTPException(
            status_code=400,
            detail="Email is not registered with us.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status == AccountStatus.INACTIVE:
        raise HTTPException(
            status_code=400,
            detail="you are not allwed to entre this application right now , contact the admin.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    password = hash_password(data.password)
    if not verify_password(data.password , user.password) :
        raise HTTPException(
            status_code=400,
            detail="Invalid Login Credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    _verify_user_access(user=user)

    return await _get_user_token(user=user)


async def get_refresh_token(token, db: Session):

    payload = get_token_payload(token=token)
    user_id = payload.get("id", None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_user_token(user=user, refresh_token=token)


def _verify_user_access(user: UserModel):
    if user.status == userStatus.INACTIVE:
        raise HTTPException(
            status_code=401,
            detail="Your account is inactive. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _get_user_token(user: UserModel, refresh_token=None):
    payload = {"id": str(user.id)}
    access_token_expiry = timedelta(minutes=settings.JWT_EXPIRATION_MINUETS)
    access_token = await create_access_token(payload, access_token_expiry)
    if not refresh_token:
        refresh_token = await create_refresh_token(payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expiry.seconds,  # in seconds
    )
