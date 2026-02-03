from pydantic import BaseModel
from typing import Optional

class CartItemCreate(BaseModel):
    product_id: int
    quantity: Optional[int] = 1  

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True  
