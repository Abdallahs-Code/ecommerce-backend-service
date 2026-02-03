from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["Products"], dependencies=[Depends(get_current_user)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        logger.warning(f"Category with id {product.category_id} not found when trying to create product")
        raise HTTPException(status_code=404, detail="Category not found")
    
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    logger.info(f"Product created with ID {new_product.id} and name '{new_product.name}'")

    return new_product

@router.get("/", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of items to return"),
):
    products = db.query(Product).offset(skip).limit(limit).all()
    logger.info(f"Fetched products with skip={skip} and limit={limit}, total fetched: {len(products)}")
    return products

@router.get("/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        logger.warning(f"Product with id {id} not found when trying to retrieve it")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Product retrieved with ID {product.id} and name '{product.name}'")
    return product

@router.patch("/{id}", response_model=ProductResponse)
def update_product(id: int, update_data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        logger.warning(f"Product with id {id} not found when trying to update it")
        raise HTTPException(status_code=404, detail="Product not found")

    update_fields = update_data.dict(exclude_unset=True)
    changed_fields = {}
    
    for key, value in update_fields.items():
        old_value = getattr(product, key)
        if value != old_value:
            changed_fields[key] = {"old": old_value, "new": value}
            setattr(product, key, value)

    if changed_fields:
        db.commit()
        db.refresh(product)
        changes_str = ", ".join([f"{k}: {v['old']} -> {v['new']}" for k, v in changed_fields.items()])
        logger.info(f"Product {id} updated: {changes_str}")

    return product

@router.delete("/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        logger.warning(f"Product with id {id} not found when trying to delete it")
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    logger.info(f"Product with id {id} deleted successfully")
    
    return {"message": "Product deleted successfully"}