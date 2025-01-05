from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product as ProductModel
from app.models import  Category,Pricelist,PricelistLine
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.product import ProductCreate, ProductUpdate,Product_with_Pricelist_Out

async def get_products(db: Session, page: int, page_size: int):
    offset = (page - 1) * page_size
    products_query = db.query(ProductModel).offset(offset).limit(page_size)
    total_records = db.query(ProductModel).count()

    products = products_query.all()
    return products, total_records


async def create_product(db: Session, product_data: ProductCreate):
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {product_data.category_id} does not exist."
        )

    new_product = ProductModel(**product_data.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

async def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)
    try:
        db.commit()
    except Exception as e:
        print(e)
        raise Exception
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist."
        )
    return product


async def search_products_in_db(db: Session, name: str, category_id: int, min_price: float, max_price: float):
    query = db.query(ProductModel)

    if name:
        query = query.filter(ProductModel.name.ilike(f"%{name}%"))
    if category_id:
        query = query.filter(ProductModel.category_id == category_id)
    if min_price is not None:
        query = query.filter(ProductModel.unit_price >= min_price)
    if max_price is not None:
        query = query.filter(ProductModel.unit_price <= max_price)

    return query.all()



async def get_products_by_category_id(db: Session, category_id: int, page: int, page_size: int):
    offset = (page - 1) * page_size
    products_query = db.query(ProductModel).filter(ProductModel.category_id == category_id).offset(offset).limit(page_size)
    total_records = db.query(ProductModel).filter(ProductModel.category_id == category_id).count()

    products = products_query.all()
    return products, total_records





async def bulk_upload_products_to_db(db: Session, products: list[ProductCreate]):
    try:
        new_products = [ProductModel(**product_data.dict()) for product_data in products]
        db.bulk_save_objects(new_products)
        db.commit()
        return new_products
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def get_products_with_stock(db: Session):
    products = db.query(ProductModel).filter(ProductModel.quantity > 0).all()
    return products

#get_products_with_no_stock
async def get_products_with_no_stock(db: Session):
    products = db.query(ProductModel).filter(ProductModel.quantity == 0).all()
    return products


async def delete_product(db: Session, product_id: int):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}



async def bulk_delete_products(db: Session, product_ids: list[int]):
    products = db.query(ProductModel).filter(ProductModel.id.in_(product_ids)).all()
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products found"
        )
    for product in products:
        db.delete(product)
    db.commit()
    return {"message": "Products deleted successfully"}



async def get_products_with_pricelist(db: Session,pricelist_id, page: int, page_size: int):
    offset = (page - 1) * page_size
    products_query = db.query(ProductModel).offset(offset).limit(page_size)
    total_records = db.query(ProductModel).count()

    products = products_query.all()
    pricelist_line = db.query(PricelistLine).filter(PricelistLine.pricelist_id == pricelist_id).first()
    return_products = []
    for product in products:
        if product.id == pricelist_line.product_id:
            return_products.append(Product_with_Pricelist_Out(
                **product.__dict__,
                new_price=pricelist_line.new_price,

            ))
        else:
            return_products.append(Product_with_Pricelist_Out(
                **product.__dict__,

            ))
    return return_products, total_records