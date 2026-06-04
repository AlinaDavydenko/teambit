from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

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
