from pydantic import BaseModel
from typing import List
from app.schemas.cart_item import CartItemResponse

class CartCreate(BaseModel):
    pass 

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = [] 

    class Config:
        from_attributes = True