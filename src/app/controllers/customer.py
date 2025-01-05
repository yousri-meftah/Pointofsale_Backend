from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.customer import Customer as CustomerModel
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.customer import CustomerCreate, CustomerUpdate

def list_customers(db: Session, page: int, page_size: int):
    try:
        offset = (page - 1) * page_size
        customers = db.query(CustomerModel).offset(offset).limit(page_size).all()
        total_records = db.query(CustomerModel).count()
        return customers, total_records
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving customers."
        ) from e



def create_customer(db: Session, customer: CustomerCreate):
    try:
        new_customer = CustomerModel(
            name=customer.name,
            email=customer.email,
            pricelist_id=customer.pricelist_id
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the customer."
        ) from e



def update_customer(db: Session, customer_id: int, customer: CustomerUpdate):
    existing_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    if customer.name:
        existing_customer.name = customer.name
    if customer.email:
        existing_customer.email = customer.email
    if customer.pricelist_id:
        existing_customer.pricelist_id = customer.pricelist_id
    db.commit()
    db.refresh(existing_customer)
    return existing_customer



def delete_customer(db: Session, customer_id: int):
    try:
        existing_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not existing_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        db.delete(existing_customer)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the customer."
        ) from e


def bulk_create_customers(db: Session, customers: list[CustomerCreate]):
    try:
        new_customers = []
        for customer_data in customers:
            new_customer = CustomerModel(
                name=customer_data.name,
                email=customer_data.email,
                pricelist_id=customer_data.pricelist_id
            )
            db.add(new_customer)
            new_customers.append(new_customer)
        db.commit()
        return new_customers
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding customers."
        ) from e



def customer_by_id( db: Session,id : int):
    res =  db.query(CustomerModel).filter(CustomerModel.id == id).first()
    return res
