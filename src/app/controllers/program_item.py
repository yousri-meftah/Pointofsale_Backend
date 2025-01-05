from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.program_item import ProgramItem
from app.schemas.program_item import ProgramItemCreate, ProgramItemUpdate

async def get_program_items(db: Session):
    return db.query(ProgramItem).all()

async def create_program_item(db: Session, program_item_data: ProgramItemCreate):
    new_program_item = ProgramItem(**program_item_data.dict())
    db.add
    db.add(new_program_item)
    db.commit()
    db.refresh(new_program_item)
    return new_program_item

async def update_program_item(db: Session, program_item_id: int, program_item_data: ProgramItemUpdate):
    program_item = db.query(ProgramItem).filter(ProgramItem.id == program_item_id).first()
    if not program_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program item not found")

    for key, value in program_item_data.dict(exclude_unset=True).items():
        setattr(program_item, key, value)

    db.commit()
    db.refresh(program_item)
    return program_item

async def delete_program_item(db: Session, program_item_id: int):
    program_item = db.query(ProgramItem).filter(ProgramItem.id == program_item_id).first()
    if not program_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program item not found")

    db.delete(program_item)
    db.commit()
    return program_item
