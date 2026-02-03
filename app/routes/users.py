from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.utils.auth import hash_password
from app.schemas.user import UserResponse, UserUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["Users"], dependencies=[Depends(get_current_user)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=UserResponse)
def get_user_details(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        logger.warning(f"User with id {current_user_id} not found when trying to retrieve details")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Retrieved user details for user ID {user.id}")
    return user

@router.patch("/", response_model=UserResponse)
def update_user_details(
    update_data: UserUpdate,  
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        logger.warning(f"User with id {current_user_id} not found when trying to update details")
        raise HTTPException(status_code=404, detail="User not found")

    updated_fields = []

    if update_data.username is not None and update_data.username != user.username:
        old_username = user.username
        user.username = update_data.username
        updated_fields.append(f"username: '{old_username}' -> '{update_data.username}'")

    if update_data.password is not None:
        user.password = hash_password(update_data.password)
        updated_fields.append("password: <updated>")

    if updated_fields:
        db.commit()
        db.refresh(user)
        logger.info(f"User {user.id} updated: {', '.join(updated_fields)}")
    
    return user