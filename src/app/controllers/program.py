from sqlalchemy.orm import Session , joinedload
from fastapi import HTTPException, status
from app.models.program import Program
from app.schemas.program import ProgramCreate, ProgramUpdate,ProgramOut,programItem_out,ProgramDetails
from app.utils import generate_random_code
from app.models.program_item import ProgramItem
from app.models.product import Product as ProductModel
from app.enums import CodeStatusEnum,ProgramTypeEnum
from app.models.order import Order

from typing import List, Dict

async def get_programs(db: Session):
    return db.query(Program).all()


async def create_program_with_items(
    program_data: ProgramCreate,
    db: Session ):
    try:
        new_program = Program(
            name=program_data.name,
            description=program_data.description,
            program_type=program_data.program_type,
            start_date=program_data.start_date,
            end_date=program_data.end_date,
            discount=program_data.discount,
            product_buy_id=program_data.product_buy_id,
            product_get_id=program_data.product_get_id,
            program_status=program_data.program_status
        )

        db.add(new_program)
        db.flush()
        db.refresh(new_program)
        if program_data.count==None or program_data.count==0:
            countt = 1
        else:
            countt=program_data.count
        program_items = [
            ProgramItem(
                code=generate_random_code(),
                status=CodeStatusEnum.ACTIVE,
                program_id=new_program.id,
                order_id=None
            )
            for _ in range(countt)
        ]

        db.bulk_save_objects(program_items)
        db.commit()

        return new_program

    except Exception as e:
        db.rollback()
        raise e




async def update_program(db: Session, program_id: int, program_data: ProgramUpdate):
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    for key, value in program_data.dict(exclude_unset=True).items():
        setattr(program, key, value)

    db.commit()
    db.refresh(program)
    return program

def delete_program(program_id: int, db: Session):
    # Fetch the program with associated program items
    program = db.query(Program).filter(Program.id == program_id).options(joinedload(Program.program_item)).first()

    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    # Delete associated program items
    if program.program_item:
        for item in program.program_item:
            db.delete(item)

    # Delete the program
    db.delete(program)
    db.commit()


def get_all_program_items(program_id: int, db: Session) -> list[ProgramItem]:
    return db.query(ProgramItem).filter(ProgramItem.program_id == program_id).all()

def get_all_programs_with_items(db: Session) -> Dict[int, List[ProgramItem]]:
    programs = db.query(Program).options(joinedload(Program.program_item)).all()
    program_map = {program.id: program.program_item for program in programs}
    return program_map

def get_coupon_program(db: Session) -> List[programItem_out]:
    program_items = db.query(ProgramItem).join(Program).filter(Program.program_type == "DISCOUNT").all()
    program_list = [programItem_out(
        id=item.id,
        code=item.code,
        status=item.status,
        order_id=item.order_id,
        discount=item.program.discount,
        product_buy_id=item.program.product_buy_id,
        product_get_id=item.program.product_get_id
    ) for item in program_items]
    return program_list


def get_BUTXGETY_program(db: Session) -> List[programItem_out]:
    program_items = db.query(Program).filter(Program.program_type == "BUYXGETY").all()
    program_list = [programItem_out(
        id=item.id,
        code = str(item.id),
        status=CodeStatusEnum.ACTIVE,
        discount=item.discount,
        product_buy_id=item.product_buy_id,
        product_get_id=item.product_get_id
    ) for item in program_items]
    return program_list



def calcul_program(product_ids : list[int], program_codes : list[str],total_price : float, db):
    results = {}
    total_discount = 0

    for code in program_codes:
        program_item = db.query(ProgramItem).filter_by(code=code).first()
        if not program_item or program_item.status != CodeStatusEnum.ACTIVE:
            results[code] = ProgramDetails(
                status="Invalid or inactive",
                discount=0
            )
            continue

        program = program_item.program
        discount = 0

        if program.program_type == ProgramTypeEnum.DISCOUNT:
            discount = total_price * (program.discount / 100)
        elif program.program_type == ProgramTypeEnum.BUYXGETY:
            buy_product_in_order = program.product_buy_id in product_ids

            if buy_product_in_order:
                get_product_price = db.query(ProductModel).filter_by(id=program.product_get_id).first()

                discount = get_product_price.unit_price

        results[code] = {
            "status": "Valid",
            "program_type": program.program_type,
            "discount": discount
        }

    return results
