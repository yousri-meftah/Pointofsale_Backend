from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.order_line import OrderLine as OrderLineModel
from app.schemas.order_line import OrderLineCreate, OrderLineUpdate

async def get_order_lines(db: Session):
    return db.query(OrderLineModel).all()

async def create_order_line(db: Session, order_line_data: OrderLineCreate):
    new_order_line = OrderLineModel(**order_line_data.dict())
    db.add(new_order_line)
    db.commit()
    db.refresh(new_order_line)
    return new_order_line

async def update_order_line(db: Session, order_line_id: int, order_line_data: OrderLineUpdate):
    order_line = db.query(OrderLineModel).filter(OrderLineModel.id == order_line_id).first()
    if not order_line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order line not found")
    for key, value in order_line_data.dict(exclude_unset=True).items():
        setattr(order_line, key, value)
    db.commit()
    db.refresh(order_line)
    return order_line
