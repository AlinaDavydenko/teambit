from fastapi import Depends
from fastapi import APIRouter, HTTPException
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.db.schemas import UserRegister, UserResponse, UserLogin
from app.db.models import User
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse)
def register(userdata: UserRegister, db: Session = Depends(get_db)):
    """Registration endpoint"""
    # verify Email
    existing_user_email = db.query(User).filter(User.email == userdata.email).first()
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # verify nikname
    existing_user_nickname = (
        db.query(User).filter(User.nickname == userdata.nickname).first()
    )
    if existing_user_nickname:
        raise HTTPException(status_code=400, detail="Nickname already taken")

    # password to hash
    hashed_password = hash_password(userdata.password)

    # Save userdata to database

    new_user = User(
        first_name=userdata.first_name,
        last_name=userdata.last_name,
        nickname=userdata.nickname,
        email=userdata.email,
        password=hashed_password,
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)  # to get the ID assigned by the database

    return UserResponse.model_validate(new_user)


@router.post("/login")
def login(userdata: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint"""

    # Search user via Email
    user = db.query(User).filter(User.email == userdata.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email is not found")
    else:
        # Find a password
        user_hash_password = user.password

    # Check if user login password right
    check_password = verify_password(userdata.password, user_hash_password)
    if not check_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    jwt_token = create_access_token({"user_id": user.user_id})

    return jwt_token


# 2. POST /auth/login — логин:

# Получить данные (UserLogin)
# Найти пользователя по email — если не найден вернуть HTTPException(401)
# Проверить пароль через verify_password — если не совпадает вернуть HTTPException(401)
# Создать JWT токен через create_access_token
# Вернуть токен
