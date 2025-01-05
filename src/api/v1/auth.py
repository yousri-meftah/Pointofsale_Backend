from fastapi import APIRouter, status, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from app.controllers.auth import get_token, get_refresh_token
from typing import Optional
from app.models import black_list_token as BlacklistedToken
from app.schemas.base import OurBaseModelOut
from app.schemas.auth import ActivateAccount,resetPassword ,forgetPassword
from app.controllers.employee import activate_account as activate_account_function,reset_password,send_reset_password_email
from app.schemas.employee import UserOut
from app import models
from app.services.token import get_current_user

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/login", status_code=status.HTTP_200_OK)
async def authenticate_user(
    data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return await get_token(data=data, db=db)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    refresh_token: str = Header(), db: Session = Depends(get_db)
):
    return await get_refresh_token(token=refresh_token, db=db)

@router.post("/logout")
def logout(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token:
        db.add(BlacklistedToken(token=token))
        db.commit()
        return {"message": "Logout successful"}
    else:
        raise HTTPException(status_code=400, detail="Token header not provided")


@router.post("/activate", response_model=OurBaseModelOut)
async def activate_employee(activate_account: ActivateAccount, db: Session = Depends(get_db)):
    if activate_account.password != activate_account.confirmPass:
        return OurBaseModelOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Passwords do not match."
        )
    try:
        activate = await activate_account_function(db, activate_account.password, activate_account.code)
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred during activation."
        )

    return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Employee activated successfully.",
        )

@router.post("/reset-password")
def reset(
    reset_data: resetPassword,
    db: Session = Depends(get_db)
):
    if reset_data.password != reset_data.confirmPass:
        return OurBaseModelOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Passwords do not match."
        )

    try:
        reset_password(db, reset_data.code, reset_data.password)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Password reset successfully.",
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred during password reset."
        )


@router.post("/forget_password", response_model=OurBaseModelOut)
async def change_password(
    forget_data: forgetPassword,
    db: Session = Depends(get_db)
):
    try:
        await send_reset_password_email(forget_data.email, db)

    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while sending reset password email. which is "+str(e)
        )

    return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Reset password email sent successfully.",
        )

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserOut
)
def get_user_detail(User: models.employee = Depends(get_current_user)):
    if User is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    account_status = User.status.name
    roles = User.Employee_roles
    employee_fields = User.__dict__
    employee_fields.pop('status')
    employee_fields.pop('password')
    return UserOut(
        **employee_fields,
        account_status=account_status,
        roles=[role.role.name for role in roles],
        status = status.HTTP_200_OK,
        message = "User found."
    )
