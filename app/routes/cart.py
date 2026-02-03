from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.utils.dependencies import get_current_user
from app.schemas.cart import CartCreate, CartResponse
from app.schemas.cart_item import CartItemResponse

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
        raise HTTPException(status_code=400, detail="User already has a cart")

    cart = Cart(user_id=current_user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

@router.delete("/")
def delete_cart(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == current_user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    db.delete(cart)
    db.commit()
    return {"message": "Cart deleted successfully"}


@router.get("/items/{cart_id}", response_model=list[CartItemResponse])
def get_cart_items(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    return items