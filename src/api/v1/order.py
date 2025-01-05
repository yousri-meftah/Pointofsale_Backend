from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.order import Order, OrderOut,OrderCreate
from app.controllers.order import list_orders, create_order, update_order,get_order_products
from app.services.token import get_current_user
from app.models.product import Product
from app.schemas.order import PriceCalculationOut,OrderIn,CalculatedOrder,OrdersOut,order_details
from app.enums import Role
from app.models.order import Order as OrderModel
from app.models import Customer
from app.models import Pricelist as PricelistModel
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker
from app.models.session import Session as SessionModel
router = APIRouter(
    dependencies=[Depends(oauth2_scheme)]
)

@router.get("/", response_model=OrdersOut)
def list_orders_route(
    db: DBSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    try:
        orders, total_records = list_orders(db, page, page_size)
        total_pages = (total_records + page_size - 1) // page_size
        
        res = []
        for order in orders:
            pr = []
            for i in order.program_item:
                pr.append(i.code)
            res.append(OrderOut(
                id=order.id,
                number = order.number,
                customer_id= order.customer_id,
                session_id= order.session_id,
                created_on = order.created_on,
                total_price = order.total_price,
                pricelist_id= order.pricelist_id,
                program_item = pr
            ))

        return OrdersOut(
            status=status.HTTP_200_OK,
            message="Orders retrieved successfully.",
            list=res,
            page_number=page,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving orders."
        )


#@router.post("/orders/calculate", response_model=CalculatedOrder)
async def calculate_order_price(
    order_in: OrderIn,
    db: DBSession = Depends(get_db)
):
    try:
        product_ids = [line.product_id for line in order_in.order_lines]
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        if len(products) != len(product_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more products not found")

        order_items = [{"product_id": line.product_id, "quantity": line.quantity, "price": product.price} for line, product in zip(order_in.order_lines, products)]
        pricing_result = calculate_order_price(order_items, order_in.customer_id, order_in.program_code, db)

        return pricing_result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate order price")



@router.post("/", response_model=OurBaseModelOut)
async def create_order_endpoint(
    order: OrderCreate,
    db: DBSession = Depends(get_db),
):
    try:
        """session = db.query(SessionModel).filter(SessionModel.id == OrderCreate.session_id).first()
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {OrderCreate.session_id} not found."
            )
        if(session.closed_at is not None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session with ID {OrderCreate.session_id} is already closed."
            )"""

        create_order(db, order)

        return OurBaseModelOut(
            status=status.HTTP_201_CREATED,
            message="Order created successfully.",
        )
    except HTTPException as e:
        db.rollback()
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        db.rollback()
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating order."
        )

@router.get("/orders/{order_id}/products", response_model=order_details)
def read_order_products(order_id: int, db: DBSession = Depends(get_db)):
    try:
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        products,code = get_order_products(db, order)
        
        pricelist_id = order.pricelist_id
        pricelist = db.query(PricelistModel).filter(PricelistModel.id==pricelist_id).first()
        pricelist_name = pricelist.name if pricelist else None
        customer_id = order.customer_id
        customer = db.query(Customer).filter(Customer.id==customer_id).first()
        customer_name=None
        if customer :
            customer_name=customer.name
        return order_details(
            status=status.HTTP_200_OK,
            code = code,
            message="Order products retrieved successfully.",
            pricelist_name=pricelist_name,
            customer_name=customer_name,
            total_price=order.total_price,
            session_id=order.session_id,
            products=products
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )



#@router.patch("/{order_id}", response_model=OurBaseModelOut)
async def update_order_endpoint(order_id: int, order: Order, db: DBSession = Depends(get_db)):
    try:
        updated_order = await update_order(db, order_id, order)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Order updated successfully.",
            data=updated_order
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating order."
        )
