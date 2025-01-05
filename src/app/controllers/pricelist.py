from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.pricelist import Pricelist
from app.models.pricelist_line import PricelistLine
from app.models.product import Product
from app.schemas.base import OurBaseModelOut
from app.schemas.pricelist import PricelistCreate, PricelistUpdate,PricelistLineOut_base
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

def get_pricelists(db: Session):
    pricelists = db.query(Pricelist).all()
    return pricelists


def get_pricelist(db: Session, pricelist_id: int):
    try:
        pricelist = db.query(Pricelist).filter(Pricelist.id == pricelist_id).first()
        if not pricelist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="price list not found")
        return pricelist
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="price list not found")


def create_pricelist(db: Session, pricelist: PricelistCreate):
    try:
        db_pricelist = Pricelist(**pricelist.dict())
        db.add(db_pricelist)
        db.commit()
        db.refresh(db_pricelist)
        return db_pricelist
    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="something went wrong")


def update_pricelist(db: Session, pricelist_id: int, pricelist_update: PricelistUpdate):
    try:
        pricelist = db.query(Pricelist).filter(Pricelist.id == pricelist_id).first()
        if not pricelist:
            raise NoResultFound("Pricelist not found")
        for key, value in pricelist_update.dict().items():
            if value :
                setattr(pricelist, key, value)
        db.commit()
        db.refresh(pricelist)
        return pricelist
    except NoResultFound as e:
        return OurBaseModelOut(status=status.HTTP_404_NOT_FOUND, message=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        return OurBaseModelOut(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))

def delete_pricelist(db: Session, pricelist_id: int):
    try:
        pricelist = db.query(Pricelist).filter(Pricelist.id == pricelist_id).first()
        if not pricelist:
            raise NoResultFound("Pricelist not found")
        db.delete(pricelist)
        db.commit()
    except NoResultFound as e:
        return OurBaseModelOut(status=status.HTTP_404_NOT_FOUND, message=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        return OurBaseModelOut(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))



def get_all_pricelists_with_lines(db: Session):
    try:
        pricelists = db.query(Pricelist).all()
        result = {}
        for pricelist in pricelists:
            pricelist_lines = db.query(PricelistLine).filter(PricelistLine.pricelist_id == pricelist.id).all()
            lines = []
            for line in pricelist_lines:
                product = db.query(Product).filter(Product.id == line.product_id).first()
                if product :
                    lines.append(PricelistLineOut_base(**line.__dict__, product_name=product.name))


            #product = db.query(Productmodel).filter(Productmodel.id == pricelist.product_id).first()
            result[pricelist.id] = lines
            #result[pricelist.id]["name"] = product.name
        return result
    except SQLAlchemyError as e:
        return OurBaseModelOut(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))




def delete_pricelistline(pricelist_line_id:int  , db:Session):
    try:
        pricelist_line = db.query(PricelistLine).filter(PricelistLine.id == pricelist_line_id).first()
        if not pricelist_line:
            raise NoResultFound("Pricelist line not found")
        db.delete(pricelist_line)
        db.commit()
    except NoResultFound as e:
        return OurBaseModelOut(status=status.HTTP_404_NOT_FOUND, message=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        return OurBaseModelOut(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))

