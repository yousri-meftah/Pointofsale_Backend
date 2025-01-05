from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.pricelist_line import PricelistLine
from app.schemas.pricelist_line import PricelistLineCreate, PricelistLineUpdate
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from app.schemas.base import OurBaseModelOut

def create_pricelist_line(db: Session, pricelist_line: PricelistLineCreate):
    try:
        db_pricelist_line = PricelistLine(**pricelist_line.dict())
        db.add(db_pricelist_line)
        db.commit()
        db.refresh(db_pricelist_line)
        return db_pricelist_line
    except SQLAlchemyError as e:
        db.rollback()
        return OurBaseModelOut(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))



def update_pricelist_line(db: Session, pricelist_line_id: int, pricelist_line_update: PricelistLineUpdate):
    try:
        pricelist_line = db.query(PricelistLine).filter(PricelistLine.id == pricelist_line_id).first()
        if not pricelist_line:
            raise NoResultFound("PricelistLine not found")
        for key, value in pricelist_line_update.dict().items():
            if value:
                setattr(pricelist_line, key, value)
        db.commit()
        db.refresh(pricelist_line)
        return pricelist_line
    except NoResultFound as e:
        return OurBaseModelOut(status=status.HTTP_404_NOT_FOUND, message=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        return OurBaseModelOut(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))



def delete_pricelist_line(db: Session, pricelist_line_id: int):
    try:
        pricelist_line = db.query(PricelistLine).filter(PricelistLine.id == pricelist_line_id).first()
        if not pricelist_line:
            raise NoResultFound("PricelistLine not found")
        db.delete(pricelist_line)
        db.commit()
        return pricelist_line
    except NoResultFound as e:
        return OurBaseModelOut(status=status.HTTP_404_NOT_FOUND, message=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        return OurBaseModelOut(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
