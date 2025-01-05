from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.pricelist import PricelistCreate, PricelistUpdate, PricelistOut,PricelistsPagedResponse , pricelist_with_lines
from app.controllers.pricelist import get_pricelists, create_pricelist, update_pricelist,delete_pricelist,get_all_pricelists_with_lines,delete_pricelistline
from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker

allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.ADMIN,Role.VENDOR])
router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.get("/", response_model=PricelistsPagedResponse)
def list_pricelists(
    db: DBSession = Depends(get_db),
    ):
    try:
        pricelists = get_pricelists(db)

        return PricelistsPagedResponse(
            status=status.HTTP_200_OK,
            message="pricelist retrieved successfully.",
            items=pricelists
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving pricelists."
        )

@router.post("/pricelists", response_model=PricelistOut)
def create_pricelist_endpoint(
    pricelist: PricelistCreate, db: DBSession = Depends(get_db)
):
    try:
        result = create_pricelist(db, pricelist)
        return PricelistOut(
            status=status.HTTP_201_CREATED,
            message="Pricelist created successfully.",
            **result.__dict__
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the pricelist."
        )

@router.patch("/{pricelist_id}", response_model=PricelistOut)
def update_existing_pricelist(
    pricelist_id: int, pricelist: PricelistUpdate, db: DBSession = Depends(get_db),
):
    try:
        updated_pricelist = update_pricelist(db, pricelist_id, pricelist)
        return PricelistOut(
            status=status.HTTP_200_OK,
            message="Pricelist updated successfully.",
            **updated_pricelist.__dict__
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating pricelist."
        )



@router.get("/pricelists_with_lines", response_model=pricelist_with_lines)
async def get_all_pricelists_with_lines_endpoint(
    db: DBSession = Depends(get_db)
):
    try:
        result = get_all_pricelists_with_lines(db)
        return pricelist_with_lines(
            status=status.HTTP_200_OK,
            message="Pricelists retrieved successfully.",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving all pricelists with their lines."
        )


@router.delete("/pricelist_line/{pricelist_line_id}" , response_model=OurBaseModelOut)
def delete_pricelist_line(pricelist_line_id :int , db : DBSession = Depends(get_db)):
    try:
        delete_pricelistline(pricelist_line_id,db)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Pricelist deleted successfully."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the pricelist."
        )
