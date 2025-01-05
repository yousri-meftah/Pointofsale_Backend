from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from sqlalchemy.exc import SQLAlchemyError
async def get_categories(db: Session):
    try:
        result = db.query(Category).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving categories ")
    return result


async def create_category(db: Session, category_data: CategoryCreate):
    cat = category_data.__dict__
    new_category = Category(**cat)

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="An error occurred while creating the category: " + str(e))

async def create_categories(categories_data: list[CategoryCreate], db: Session):
    try:
        new_categories = [Category(**category.__dict__) for category in categories_data]
        db.bulk_save_objects(new_categories)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    return new_categories

async def update_category(db: Session, category_id: int, category_data: CategoryUpdate):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for key, value in category_data.dict(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category

async def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.delete(category)
    db.commit()
    return category


async def delete_category_by_name_or_id(db: Session, identifier: str):
    if identifier.isdigit():
        category = db.query(Category).filter(Category.id == int(identifier)).first()
    else:
        category = db.query(Category).filter(Category.name == identifier).first()

    if not category:
        return None

    db.delete(category)
    db.commit()
    return category