from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.order_line import OrderLine, OrderLineOut
from app.controllers.order_line import get_order_lines, create_order_line, update_order_line

from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker
allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.ADMIN])

router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.get("/", response_model=OurBaseModelOut)
async def list_order_lines(db: DBSession = Depends(get_db)):
    try:
        order_lines = await get_order_lines(db)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Order lines retrieved successfully.",
            data=order_lines
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving order lines."
        )

@router.post("/", response_model=OurBaseModelOut)
async def create_order_line_endpoint(order_line: OrderLine, db: DBSession = Depends(get_db)):
    try:
        new_order_line = await create_order_line(db, order_line)
        return OurBaseModelOut(
            status=status.HTTP_201_CREATED,
            message="Order line created successfully.",
            data=new_order_line
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating order line."
        )

@router.patch("/{order_line_id}", response_model=OurBaseModelOut)
async def update_order_line_endpoint(order_line_id: int, order_line: OrderLine, db: DBSession = Depends(get_db)):
    try:
        updated_order_line = await update_order_line(db, order_line_id, order_line)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Order line updated successfully.",
            data=updated_order_line
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating order line."
        )
