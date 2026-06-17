from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from app.db.schemas import UserResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/users")


@router.get("/search", response_model=list[UserResponse])
def search_users(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Search users by nickname or email, excluding the current user"""
    pattern = f"%{query}%"

    users = (
        db.query(User)
        .filter(
            (User.nickname.ilike(pattern)) | (User.email.ilike(pattern)),
            User.user_id != current_user.user_id,
        )
        .limit(10)
        .all()
    )

    return users
