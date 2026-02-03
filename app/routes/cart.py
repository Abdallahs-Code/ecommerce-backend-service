from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.utils.dependencies import get_current_user
from app.schemas.cart import CartCreate, CartResponse
from app.schemas.cart_item import CartItemResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cart", tags=["Cart"], dependencies=[Depends(get_current_user)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CartResponse)
def create_cart(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user_cart = db.query(Cart).filter(Cart.user_id == current_user_id).first()
    if user_cart:
        logger.warning(f"User {current_user_id} already has a cart with ID {user_cart.id}")
        raise HTTPException(status_code=400, detail="User already has a cart")

    cart = Cart(user_id=current_user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    logger.info(f"Cart with id {cart.id} created for user {current_user_id}")

    return cart

@router.delete("/")
def delete_cart(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == current_user_id).first()
    if not cart:
        logger.warning(f"User {current_user_id} attempted to delete a non-existent cart")
        raise HTTPException(status_code=404, detail="Cart not found")

    db.delete(cart)
    db.commit()
    logger.info(f"Cart with id {cart.id} deleted for user {current_user_id}")

    return {"message": "Cart deleted successfully"}


@router.get("/items/{cart_id}", response_model=list[CartItemResponse])
def get_cart_items(
    cart_id: int, 
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=50, description="Max items to return")
):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        logger.warning(f"Cart with id {cart_id} not found when fetching cart items")
        raise HTTPException(status_code=404, detail="Cart not found")

    items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.info(f"Fetched items for cart id {cart_id} with skip={skip}, limit={limit}, total fetched: {len(items)}")
    
    return items