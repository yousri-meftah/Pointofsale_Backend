from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.pricelist_line import PricelistLineCreate, PricelistLineUpdate, PricelistLineOut
from app.controllers.pricelist_line import  create_pricelist_line, update_pricelist_line
from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker

allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.ADMIN])
router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)


@router.post("/", response_model=PricelistLineOut)
def create_new_pricelist_line(
    pricelist_line: PricelistLineCreate, db: DBSession = Depends(get_db)
):
    try:
        new_pricelist_line = create_pricelist_line(db, pricelist_line)
        return PricelistLineOut(
            status=status.HTTP_201_CREATED,
            message="Pricelist line created successfully.",
            **new_pricelist_line.__dict__
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating pricelist line."
        )

@router.patch("/{pricelist_line_id}", response_model=PricelistLineOut)
def update_existing_pricelist_line(
    pricelist_line_id: int, pricelist_line: PricelistLineUpdate, db: DBSession = Depends(get_db)
):
    try:
        updated_pricelist_line = update_pricelist_line(db, pricelist_line_id, pricelist_line)
        return PricelistLineOut(
            status=status.HTTP_200_OK,
            message="Pricelist line updated successfully.",
            **updated_pricelist_line.__dict__
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating pricelist line."
        )


