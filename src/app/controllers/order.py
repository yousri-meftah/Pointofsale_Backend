from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.order import Order as OrderModel
from app.schemas.order import OrderCreate, OrderUpdate
from app.models.product import Product as ProductModel
from app.models.customer import Customer as CustomerModel
from app.models.pricelist_line import PricelistLine as PriceListLineModel
from app.models.program_item import ProgramItem as ProgramItemModel
from app.enums import CodeStatusEnum, ProgramTypeEnum
from app.models.order_line import OrderLine as OrderLineModel
from app.models.program import Program
from app.models.pricelist_line import PricelistLine
from app.schemas.order import OrderIn,CalculatedOrder,DiscountDetail,OrderLineSchema



def list_orders(db: Session, page: int, page_size: int):
    offset = (page - 1) * page_size
    query = db.query(OrderModel)
    total_records = query.count()
    orders = query.offset(offset).limit(page_size).all()
    return orders, total_records


"""def create_order(db: Session, order_data: OrderCreate):
    order_lines_data = order_data.products_ids

    # Validate all product IDs before proceeding
    product_ids = [product_id for product_id, _ in order_lines_data]
    products = db.query(ProductModel).filter(ProductModel.id.in_(product_ids)).all()

    if len(products) != len(product_ids):
        invalid_product_ids = set(product_ids) - {product.id for product in products}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid product IDs: {invalid_product_ids}"
        )

    # Determine pricing based on customer price list if applicable
    customer_price_list_lines = {}
    pricelist_id = None
    if order_data.customer_id:
        customer = db.query(CustomerModel).filter_by(id=order_data.customer_id).first()
        if customer and customer.pricelist_id:
            pricelist_id = customer.pricelist_id
            price_list_lines = db.query(PriceListLineModel).filter_by(pricelist_id=pricelist_id).all()
            customer_price_list_lines = {line.product_id: line.new_price for line in price_list_lines}

    # Create the order
    new_order = OrderModel(
        customer_id=order_data.customer_id,
        session_id=order_data.session_id,
        created_on=order_data.created_on,
        total_price=0,  # Will be calculated later
        pricelist_id=pricelist_id
    )

    db.add(new_order)
    db.flush()  # Use flush instead of commit to get the new order ID

    # Create order lines
    order_lines = []
    for product_id, quantity in order_lines_data:
        unit_price = customer_price_list_lines.get(product_id, db.query(ProductModel).filter_by(id=product_id).first().unit_price)
        total_price = unit_price * quantity
        order_line = OrderLineModel(
            order_id=new_order.id,
            product_id=product_id,
            unit_price=unit_price,
            quantity=quantity,
            total_price=total_price
        )
        order_lines.append(order_line)
        new_order.total_price += total_price

    db.bulk_save_objects(order_lines)

    # Handle program functionality if program codes are provided
    if order_data.program_item_id:
        handle_program_functionality(new_order, order_lines, order_data.program_item_id, db)

    db.commit()
    db.refresh(new_order)

    return new_order

def handle_program_functionality(order, order_lines, program_codes, db):
    for code in program_codes:
        program_item = db.query(ProgramItemModel).filter_by(code=code).first()
        if not program_item or program_item.status != CodeStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or inactive program code: {code}"
            )
        program = program_item.program

        if program.program_type == ProgramTypeEnum.DISCOUNT:
            order.total_price *= (1 - program.discount / 100)
        elif program.program_type == ProgramTypeEnum.BUY_X_GET_Y:
            buy_product_in_order = False
            get_product_in_order = False
            get_product_line = None

            for line in order_lines:
                if line.product_id == program.product_buy_id:
                    buy_product_in_order = True
                if line.product_id == program.product_get_id:
                    get_product_in_order = True
                    get_product_line = line

            if buy_product_in_order:
                if get_product_in_order:
                    # If the get product is already in the order, reduce its price
                    order.total_price -= get_product_line.total_price
                    get_product_line.unit_price = 0
                    get_product_line.total_price = 0
                else:
                    # If the get product is not in the order, add it for free
                    order_line = OrderLineModel(
                        order_id=order.id,
                        product_id=program.product_get_id,
                        unit_price=0,
                        quantity=1,  # Adjust quantity as needed
                        total_price=0
                    )
                    db.add(order_line)

    db.flush()"""



def create_order(db: Session, order_data: OrderCreate):
    try:
        order_lines_data = order_data.products_ids

        # Validate product IDs
        product_ids = [product_id for product_id, _ in order_lines_data]
        products = db.query(ProductModel).filter(ProductModel.id.in_(product_ids)).all()

        if len(products) != len(product_ids):
            invalid_product_ids = set(product_ids) - {product.id for product in products}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid product IDs: {invalid_product_ids}"
            )

        # Check customer price list
        customer_price_list_lines = {}
        pricelist_id = None
        if order_data.customer_id:
            customer = db.query(CustomerModel).filter_by(id=order_data.customer_id).first()
            if customer and customer.pricelist_id:
                pricelist_id = customer.pricelist_id
                price_list_lines = db.query(PriceListLineModel).filter_by(pricelist_id=pricelist_id).all()
                customer_price_list_lines = {line.product_id: line.new_price for line in price_list_lines}

        if order_data.pricelist_id:
            pricelist_id = order_data.pricelist_id
            price_list_lines = db.query(PriceListLineModel).filter_by(pricelist_id=pricelist_id).all()
            customer_price_list_lines = {line.product_id: line.new_price for line in price_list_lines}
        # Create the order
        new_order = OrderModel(
            customer_id=order_data.customer_id,
            session_id=order_data.session_id,
            created_on=order_data.created_on,
            total_price=0,
            pricelist_id=pricelist_id
        )
        db.add(new_order)
        db.flush()  # Retrieve new_order.id

        # Create order lines
        order_lines = []
        for product_id, quantity in order_lines_data:
            product = db.query(ProductModel).filter_by(id=product_id).first()
            if product.quantity < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product_id} is out of stock"
                )
            unit_price = customer_price_list_lines.get(product_id, product.unit_price)
            total_price = unit_price * quantity
            order_line = OrderLineModel(
                order_id=new_order.id,
                product_id=product_id,
                unit_price=unit_price,
                quantity=quantity,
                total_price=total_price
            )
            order_lines.append(order_line)
            new_order.total_price += total_price

            # Update product stock
            product.quantity -= quantity
            db.add(product)

        db.bulk_save_objects(order_lines)
        db.flush()  # Flush changes to DB for order lines

        # Apply program functionality if provided
        if order_data.program_item_id:
            handle_program_functionality(new_order, order_lines, order_data.program_item_id, db)

        db.commit()  # Commit transaction

    except Exception as e:
        db.rollback()  # Rollback on any error
        print(f"Error during order creation: {e}")  # Log the error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the order."
        )




def handle_program_functionality(order, order_lines, program_codes, db):
    try:
        for code in program_codes:
            program_item = db.query(ProgramItemModel).filter_by(code=code).with_for_update().first()

            if not program_item or program_item.status != CodeStatusEnum.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid or inactive program code: {code}"
                )

            program = (
                db.query(Program)
                .join(ProgramItemModel, Program.id == ProgramItemModel.program_id)
                .filter(ProgramItemModel.code == code)
                .first()
            )

            if not program:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No associated program found for code: {code}"
                )

            # Apply program functionality
            if program.program_type == ProgramTypeEnum.DISCOUNT:
                order.total_price *= (1 - program.discount / 100)

            elif program.program_type == ProgramTypeEnum.BUYXGETY:
                buy_product_in_order = any(
                    line.product_id == program.product_buy_id for line in order_lines
                )
                get_product_line = next(
                    (line for line in order_lines if line.product_id == program.product_get_id), None
                )

                if buy_product_in_order:
                    if get_product_line:
                        # Make the 'get' product free
                        order.total_price -= get_product_line.total_price
                        get_product_line.unit_price = 0
                        get_product_line.total_price = 0
                    else:
                        # Add the 'get' product for free
                        new_order_line = OrderLineModel(
                            order_id=order.id,
                            product_id=program.product_get_id,
                            unit_price=0,
                            quantity=1,
                            total_price=0
                        )
                        db.add(new_order_line)

            # Update program item
            program_item.status = CodeStatusEnum.INACTIVE
            program_item.order_id = order.id
            db.add(program_item)

        db.flush()  # Flush changes to DB for program items

    except Exception as e:
        db.rollback()  # Rollback on any error
        print(f"Error during program functionality handling: {e}")  # Log the error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while handling program functionality."
        )




def calculate_order_price(order_in: OrderIn, db: Session) -> CalculatedOrder:
    total_price = sum(line.price * line.quantity for line in order_in.order_lines)
    discounts = []

    if order_in.pricelist_id:
        pricelist_discount, pricelist_details = apply_pricelist_discount(order_in, db)
        total_price -= pricelist_discount
        discounts.append(DiscountDetail(component='Pricelist', discount=pricelist_discount, description=pricelist_details))

    if order_in.program_code:
        program = db.query(Program).filter(Program.code == order_in.program_code).first()
        if program and program.program_type != 'DISCOUNT' and program.program_status:
            buyXgetY_discount, buyXgetY_details = apply_buyXgetY_discount(order_in, db, program)
            total_price -= buyXgetY_discount
            discounts.append(DiscountDetail(component='BuyXGetY', discount=buyXgetY_discount, description=buyXgetY_details))

    if order_in.program_code:
        program = db.query(Program).filter(Program.code == order_in.program_code).first()
        if program and program.program_type == 'DISCOUNT' and program.program_status:
            discount, discount_details = apply_discount_program(order_in, program)
            total_price -= discount
            discounts.append(DiscountDetail(component='Discount Program', discount=discount, description=discount_details))

    return CalculatedOrder(total_price=total_price, discounts=discounts)




def apply_pricelist_discount(order_in: OrderIn, db: Session):
    pricelist_lines = db.query(PricelistLine).filter(PricelistLine.pricelist_id == order_in.pricelist_id).all()
    discount = 0.0
    details = []
    for line in order_in.order_lines:
        for pricelist_line in pricelist_lines:
            if pricelist_line.product_id == line.product_id and line.quantity >= pricelist_line.min_quantity:
                discount += (line.price - pricelist_line.new_price) * line.quantity
                details.append(f"Product {line.product_id}: -${(line.price - pricelist_line.new_price) * line.quantity}")
    return discount, ', '.join(details)

def apply_buyXgetY_discount(order_in: OrderIn, db: Session, program: Program):
    discount = 0.0
    details = []
    for line in order_in.order_lines:
        if line.product_id == program.product_buy_id:
            for order_line in order_in.order_lines:
                if order_line.product_id == program.product_get_id:
                    discount += order_line.price * min(line.quantity, order_line.quantity)
                    details.append(f"Product {program.product_get_id}: -${order_line.price * min(line.quantity, order_line.quantity)}")
                    break
            else:
                details.append(f"Product {program.product_get_id} added for free")
                break
    return discount, ', '.join(details)

def apply_discount_program(order_in: OrderIn, program: Program):
    discount = 0.0
    details = []
    if program.program_type == 'DISCOUNT':
        discount = sum(line.price * line.quantity for line in order_in.order_lines) * (program.discount / 100)
        details.append(f"Discount Program: -${discount}")
    return discount, ', '.join(details)


async def update_order(db: Session, order_id: int, order_data: OrderUpdate):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    for key, value in order_data.dict(exclude_unset=True).items():
        setattr(order, key, value)
    db.commit()
    db.refresh(order)
    return order


def get_order_products(db: Session, order):
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order.id} not found"
        )
    order_id=order.id
    order_lines = db.query(OrderLineModel).filter_by(order_id=order.id).all()
    if not order_lines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No products found for order ID {order_id}"
        )
    array = []
    for line in order_lines:
        array.append(
            OrderLineSchema(
            product_id=line.product_id,
            unit_price=line.unit_price,
            quantity=line.quantity,
            total_price=line.total_price
        )
        )
    code = db.query(ProgramItemModel).join(Program,ProgramItemModel.program_id ==Program.id).filter(ProgramItemModel.order_id==order_id).first()
    if code:
        a=code.code
    else:
        a = None
    return array , a