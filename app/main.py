from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, cart, users, products, categories, cart_items
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log")
    ]
)

Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(cart_items.router)

@app.get("/")
def root():
    return {"message": "Hello, World!"}