from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from app.db.session import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.db.models import User
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    """It takes a string, returns a hash"""
    hashed_password = pwd_context.hash(password)
    return hashed_password


def verify_password(password: str, hashed: str) -> bool:
    """It checks if the password matches the hash"""
    verify_hashed_password = pwd_context.verify(password, hashed)
    return verify_hashed_password


# JWT tokens through python-jose
def create_access_token(data: dict) -> str:
    """Create a token"""
    to_encode = data.copy()  # to copy data to not change the original data in the dict

    # an expire time of the token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # to add expire time and update our dict, exp field is for expire time
    to_encode.update({"exp": expire})

    # to create the token
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Get token and database session and return an user"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
