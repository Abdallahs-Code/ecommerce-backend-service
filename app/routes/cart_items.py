from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.utils.dependencies import get_current_user
from app.schemas.cart_item import CartItemCreate, CartItemUpdate, CartItemResponse

router = APIRouter(prefix="/api/cartItems", tags=["CartItems"], dependencies=[Depends(get_current_user)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{cart_id}", response_model=CartItemResponse)
def create_cart_item(
    cart_id: int,
    cart_item: CartItemCreate, 
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == current_user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found or does not belong to user")

    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_cart_item = CartItem(
        cart_id=cart_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

@router.get("/{cart_item_id}", response_model=CartItemResponse)
def get_cart_item(cart_item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart_item

@router.patch("/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    update_data: CartItemUpdate,
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if update_data.quantity is not None:
        cart_item.quantity = update_data.quantity

    db.commit()
    db.refresh(cart_item)
    return cart_item