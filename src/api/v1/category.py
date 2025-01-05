from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.controllers.category import get_categories, create_category, update_category , create_categories , delete_category_by_name_or_id
from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker

allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.INVENTORY_MANAGER,Role.VENDOR])

router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.get("/", response_model=CategoryOut)
async def list_categories(db: DBSession = Depends(get_db)):
    try:
        categories = await get_categories(db)
        return CategoryOut(
            status=status.HTTP_200_OK,
            message="Categories retrieved successfully.",
            categories = categories
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving categories."
        )

@router.post("/", response_model=OurBaseModelOut)
async def create_new_category(
    category: CategoryCreate, db: DBSession = Depends(get_db)
):
    try:
        new_category = await create_category(db, category)
        return OurBaseModelOut(
            status=status.HTTP_201_CREATED,
            message="Category created successfully.",

        )
    except Exception as e:
        raise OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating category."
        )

@router.post("/add_categories", response_model=CategoryOut)
async def create_new_category(
    category: list[CategoryCreate], db: DBSession = Depends(get_db)
):
    try:
        new_categories = await create_categories(category , db)
        return CategoryOut(
            status=status.HTTP_201_CREATED,
            message="Category created successfully.",
            categories = new_categories
        )
    except Exception as e:
        raise OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating category."
        )


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_existing_category(
    category_id: int, category: CategoryUpdate, db: DBSession = Depends(get_db)
):
    try:
        updated_category = await update_category(db, category_id, category)
        return CategoryOut(
            status=status.HTTP_200_OK,
            message="Category updated successfully.",
            categories=[updated_category]
        )
    except HTTPException as e:
        return CategoryOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return CategoryOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating category."
        )


@router.delete("/{id}", response_model=CategoryOut)
async def delete_category(
    id: str,
    db: DBSession = Depends(get_db),
):
    try:
        result = await delete_category_by_name_or_id(db, id)
        if not result:
            return OurBaseModelOut(
                status=status.HTTP_404_NOT_FOUND,
                message="Category not found."
            )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred during category deletion."
        )

    return CategoryOut(
        status=status.HTTP_200_OK,
        message="Category deleted successfully.",
        categories=[result]
    )
