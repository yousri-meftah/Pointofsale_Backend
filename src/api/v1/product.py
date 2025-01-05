from fastapi import APIRouter, Depends, HTTPException, status ,Query
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.product import Product, ProductsOut,return_products,Products_with_pricelist_Out
from app.enums import Role
from core.database import get_db
from typing import Optional
from app.services.token import oauth2_scheme, RoleChecker
allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.INVENTORY_MANAGER])

from app.controllers.product import get_products, create_product, update_product , get_products_by_category_id ,\
    get_product , search_products_in_db ,bulk_upload_products_to_db,get_products_with_stock ,get_products_with_no_stock,\
        delete_product , bulk_delete_products,get_products_with_pricelist


router = APIRouter(
    dependencies=[Depends(oauth2_scheme) ]
)

@router.get("/", response_model=ProductsOut)
async def list_products(
    db: DBSession = Depends(get_db), 
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    try:
        products, total_records = await get_products(db, page, page_size)
        total_pages = (total_records + page_size - 1) // page_size  # Calculate total pages

        return ProductsOut(
            status=status.HTTP_200_OK,
            message="Products retrieved successfully.",
            products=products,
            page_number=page,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving products."
        )

@router.post("/", response_model=OurBaseModelOut)
async def create_product_endpoint(product: Product, db: DBSession = Depends(get_db), ok = Depends(allow_action_by_roles)):
    try:
        new_product = await create_product(db, product)
        return OurBaseModelOut(
            status=status.HTTP_201_CREATED,
            message="Product created successfully.",

        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        raise OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating product."
        )

@router.patch("/{product_id}", response_model=return_products)
async def update_product_endpoint(product_id: int, product: Product, db: DBSession = Depends(get_db),ok = Depends(allow_action_by_roles)):
    try:
        updated_product = await update_product(db, product_id, product)
        return return_products(
            status=status.HTTP_200_OK,
            message="Product updated successfully.",
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating product."
        )

@router.get("/search", response_model=return_products)
async def search_products(
    name: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: DBSession = Depends(get_db),
):
    try:
        products = await search_products_in_db(db, name, category_id, min_price, max_price)
        return return_products(
            status=status.HTTP_200_OK,
            message="Products retrieved successfully.",
            products = products
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while searching for products."
        )


@router.get("/in-stock", response_model=return_products)
async def get_products_in_stock(
    db: DBSession = Depends(get_db),
):
    try:
        products = await get_products_with_stock(db)
        return return_products(
            status=status.HTTP_200_OK,
            message="Products in stock retrieved successfully.",
            products=products
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving products in stock."
        )

@router.get("/out-stock", response_model=return_products)
async def get_products_in_stock(
    db: DBSession = Depends(get_db),
):
    try:
        products = await get_products_with_no_stock(db)
        return return_products(
            status=status.HTTP_200_OK,
            message="Products in stock retrieved successfully.",
            products=products
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving products in stock."
        )

@router.delete("/bulk-delete", response_model=OurBaseModelOut)
async def bulk_remove_products(
    product_ids: list[int],
    db: DBSession = Depends(get_db),
):
    try:
        result = await bulk_delete_products(db, product_ids)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message=result["message"]
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while deleting the products."
        )


@router.get("/{product_id}", response_model=return_products)
async def get_product_by_id(
    product_id: int,
    db: DBSession = Depends(get_db),
):
    try:
        product = get_product(db, product_id)
        return return_products(
            status=status.HTTP_200_OK,
            message="Product retrieved successfully.",
            products=[product]
        )
    except HTTPException as e:
        return return_products(
            status=e.status_code,
            message=e.detail,
            products = None
        )
    except Exception as e:
        return return_products(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An erroreee occurred while searching for products."
        )



@router.get("/category/{category_id}", response_model=ProductsOut)
async def get_products_by_category(
    category_id: int,
    db: DBSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    try:
        products, total_records = await get_products_by_category_id(db,category_id, page, page_size)
        total_pages = (total_records + page_size - 1) // page_size

        return ProductsOut(
            status=status.HTTP_200_OK,
            message="Products retrieved successfully.",
            products=products,
            page_number=page,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving products by category."
        )


@router.post("/bulk-upload", response_model=return_products)
async def bulk_upload_products(
    products: list[Product],
    db: DBSession = Depends(get_db),
):
    try:
        created_products = await bulk_upload_products_to_db(db, products)
        return return_products(
            status=status.HTTP_201_CREATED,
            message="Products uploaded successfully.",
            products=created_products
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while uploading products.",

        )



@router.delete("/{product_id}", response_model=OurBaseModelOut)
async def delete_productt(
    product_id: int,
    db: DBSession = Depends(get_db),
):
    try:
        result = await delete_product(db, product_id)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message=result["message"]
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while deleting the product."
        )




@router.get("/pricelist/{pricelist_id}", response_model=Products_with_pricelist_Out)
async def list_products(
    pricelist_id : int ,
    db: DBSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),

):
    try:
        products, total_records = await get_products_with_pricelist(db, pricelist_id,page, page_size)
        total_pages = (total_records + page_size - 1) // page_size  # Calculate total pages

        return Products_with_pricelist_Out(
            status=status.HTTP_200_OK,
            message="Products retrieved successfully.",
            products=products,
            page_number=page,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving products."
        )
