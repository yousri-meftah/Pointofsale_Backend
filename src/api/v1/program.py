from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.controllers.category import get_categories, create_category, update_category
from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker
from app.schemas.program import ProgramCreate ,ProgramItemsMap,ProgramItem_out,calculate_program,CalculateProgramRequest
from app.controllers.program import create_program_with_items,delete_program ,get_all_programs_with_items , get_all_program_items , \
    get_BUTXGETY_program , get_coupon_program,calcul_program

allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.ADMIN])

router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.post("/", response_model=OurBaseModelOut)
async def create_program_endpoint(
    program: ProgramCreate,
    db: DBSession = Depends(get_db),
):
    try:
        new_program = await create_program_with_items(program, db)
        return OurBaseModelOut(
            status=status.HTTP_201_CREATED,
            message="Program created successfully.",
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating the program."
        )

@router.get("/{program_id}/items", response_model=list[ProgramItem_out])
async def get_program_items(program_id: int, db: DBSession = Depends(get_db)):
    try:
        result =  get_all_program_items(program_id, db)
        return result
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating the program."
        )


@router.post("/calcule_program/", response_model=calculate_program)
def calcule_program(
    request: CalculateProgramRequest,
    db:DBSession = Depends(get_db) ,
):
    try:
        results = calcul_program(request.products, request.code, request.total,db)
        return calculate_program(
            status=status.HTTP_200_OK,
            message="Program calculated successfully.",
            results = results
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating the program."
        )


@router.get("/BUYXGETY_program", response_model=ProgramItemsMap)
async def get_programs_with_items(db: DBSession = Depends(get_db)):
    try:
        programs_with_items = get_BUTXGETY_program(db)
        return ProgramItemsMap(
            status=status.HTTP_200_OK,
            message="Programs with items retrieved successfully.",
            programs = programs_with_items,
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving programs with items."
        )

@router.get("/coupon_program", response_model=ProgramItemsMap)
async def get_coupon_programm(db: DBSession = Depends(get_db)):
    try:
        programs_with_items = get_coupon_program(db)
        return ProgramItemsMap(
            status=status.HTTP_200_OK,
            message="Programs with items retrieved successfully.",
            programs = programs_with_items,
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving programs with items."
        )





"""@router.delete("/{program_id}",response_model=OurBaseModelOut)
async def delete_program_endpoint(program_id: int, db: DBSession = Depends(get_db)):
    try:
        delete_program(program_id, db)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Program deleted successfully"
        )

    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating the program."
        )"""
