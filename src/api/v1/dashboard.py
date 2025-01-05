from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy import func,extract
from sqlalchemy.orm import Session as DBSession
from app.controllers.category import get_categories, create_category, update_category , create_categories , delete_category_by_name_or_id
from app.enums import Role
from app.models import Category,Product,OrderLine,Order,Employee
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker
from datetime import datetime, timedelta

allow_action_by_roles = RoleChecker([Role.ADMIN, Role.SUPER_USER])

router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.get("/revenue-per-category")
def get_revenue_per_category(db: DBSession = Depends(get_db)):
    results = (
        db.query(
            Category.name.label("category_name"),
            func.sum(OrderLine.unit_price * OrderLine.quantity).label("total_revenue")
        )
        .join(Product, Product.id == OrderLine.product_id)
        .join(Category, Category.id == Product.category_id)
        .group_by(Category.name)
        .all()
    )
    
    sum =0
    arr = []
    for i in results:
        arr.append({"category": i.category_name, "revenue": i.total_revenue})
        sum=sum+i.total_revenue

    return {
        "categories" : arr,
        "sum" : sum
    }

@router.get("/inventory-levels")
def get_inventory_levels(db: DBSession = Depends(get_db)):
    results = (
        db.query(
            Product.name.label("product_name"),
            Product.quantity.label("inventory_level")
        )
        .filter(Product.quantity > 0) 
        .all()
    )


    total_inventory = 0
    inventory_data = []

    for result in results:
        inventory_data.append({
            "product": result.product_name,
            "inventory": result.inventory_level
        })
        total_inventory += result.inventory_level

    return {
        "products": inventory_data,
        "total_inventory": total_inventory
    }


@router.get("/sales-per-month")
def get_sales_per_month(db: DBSession = Depends(get_db)):

    current_date = datetime.now()
    start_of_year = datetime(current_date.year, 1, 1)
    end_of_year = datetime(current_date.year , 12, 31) 

    results = (
        db.query(
            extract('month', Order.created_on).label("month"),
            func.sum(OrderLine.unit_price * OrderLine.quantity).label("total_sales")
        )
        .join(OrderLine, Order.id == OrderLine.order_id)
        .filter(Order.created_on >= start_of_year, Order.created_on <= end_of_year)
        .group_by(extract('month', Order.created_on))
        .order_by(extract('month', Order.created_on))
        .all()
    )

    sales_data = [{"month": int(row.month), "sales": row.total_sales} for row in results]

    return {
        "sales_per_month": sales_data
    }

@router.get("/top-selling-products/{year}/{month}")
def get_top_selling_products(
    year: int, 
    month: int,
    db: DBSession = Depends(get_db)
):
    try:

        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1)
        else:
            end_of_month = datetime(year, month + 1, 1)

        results = (
            db.query(
                Product.name.label("product_name"),
                func.sum(OrderLine.quantity).label("total_quantity_sold")
            )
            .join(OrderLine, Product.id == OrderLine.product_id)
            .join(Order, Order.id == OrderLine.order_id)
            .filter(Order.created_on >= start_of_month, Order.created_on < end_of_month)
            .group_by(Product.name)
            .order_by(func.sum(OrderLine.quantity).desc())
            .all()
        )

        top_products = [
            {"product": row.product_name, "quantity_sold": row.total_quantity_sold}
            for row in results
        ]

        return {"year": year, "month": month, "top_selling_products": top_products}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching top-selling products: {str(e)}"
        )



@router.get("/monthly-earnings")
def get_monthly_earnings_by_employee(
    year: int = Query(..., ge=2000, le=2100),
    db: DBSession = Depends(get_db)
):
    try:

        results = (
            db.query(
                Employee.firstname.label("employee_name"),
                extract('month', Order.created_on).label("month"),
                func.sum(Order.total_price).label("total_earnings")
            )
            .join(Order, Employee.id == Order.session_id) 
            .filter(extract('year', Order.created_on) == year)
            .group_by(Employee.firstname, extract('month', Order.created_on))
            .order_by(Employee.firstname, extract('month', Order.created_on))
            .all()
        )

        data = {}
        for row in results:
            employee = row.employee_name
            month = int(row.month)
            earnings = row.total_earnings

            if employee not in data:
                data[employee] = [0] * 12  
            data[employee][month - 1] = earnings

        return {
            "year": year,
            "earnings_by_employee": data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching monthly earnings: {str(e)}"
        )