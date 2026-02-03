from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/categories", tags=["Categories"], dependencies=[Depends(get_current_user)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        logger.warning(f"Category with name '{category.name}' already exists when trying to create")
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    logger.info(f"Category created with ID {new_category.id} and name '{new_category.name}'")

    return new_category

@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(10, ge=1, le=50, description="Max categories to return")
):
    categories = db.query(Category).offset(skip).limit(limit).all()
    logger.info(f"Fetched categories with skip={skip}, limit={limit}, total fetched: {len(categories)}")
    return categories

@router.get("/{id}", response_model=CategoryResponse)
def get_category(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        logger.warning(f"Category with id {id} not found when trying to retrieve it")
        raise HTTPException(status_code=404, detail="Category not found")
    logger.info(f"Category retrieved with ID {category.id} and name '{category.name}'")
    return category

@router.patch("/{id}", response_model=CategoryResponse)
def update_category(id: int, update_data: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        logger.warning(f"Category with id {id} not found when trying to update it")
        raise HTTPException(status_code=404, detail="Category not found")

    updated = False
    old_name = category.name

    if update_data.name is not None and update_data.name != category.name:
        category.name = update_data.name
        updated = True

    if updated:
        db.commit()
        db.refresh(category)
        logger.info(f"Category {id} updated: name '{old_name}' -> '{category.name}'")
        
    return category

@router.delete("/{id}")
def delete_category(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        logger.warning(f"Category with id {id} not found when trying to delete it")
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    logger.info(f"Category with id {id} deleted successfully")
    
    return {"message": "Category deleted successfully"}