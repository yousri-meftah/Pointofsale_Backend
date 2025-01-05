from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.program_item import ProgramItemCreate, ProgramItemUpdate, ProgramItemOut
from app.controllers.program_item import get_program_items, create_program_item, update_program_item
from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker

allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.ADMIN])
router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.get("/", response_model=OurBaseModelOut)
async def list_program_items(db: DBSession = Depends(get_db)):
    try:
        program_items = await get_program_items(db)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Program items retrieved successfully.",
            data=program_items
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving program items."
        )

@router.post("/", response_model=OurBaseModelOut)
async def create_new_program_item(
    program_item: ProgramItemCreate, db: DBSession = Depends(get_db)
):
    try:
        new_program_item = await create_program_item(db, program_item)
        return OurBaseModelOut(
            status=status.HTTP_201_CREATED,
            message="Program item created successfully.",
            data=new_program_item
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating program item."
        )

@router.patch("/{program_item_id}", response_model=OurBaseModelOut)
async def update_existing_program_item(
    program_item_id: int, program_item: ProgramItemUpdate, db: DBSession = Depends(get_db)
):
    try:
        updated_program_item = await update_program_item(db, program_item_id, program_item)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Program item updated successfully.",
            data=updated_program_item
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating program item."
        )
