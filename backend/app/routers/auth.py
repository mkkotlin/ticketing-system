from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, UserResponse
from app.security import create_access_token, verify_password, hash_password
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    # dependencies=[Depends(get_current_user)]
)


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.execute(
        select(User).where(
            or_(User.username == user_data.username, User.email == user_data.email)
        )
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=409, detail="username or email already exists")

    user = User(
        username = user_data.username,
        email=user_data.email,
        password_hash = hash_password(user_data.password),
        role="CUSTOMER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.username == form_data.username)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401, 
            detail="Invalid username or password"
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    token = create_access_token(user.id)
    return {"access_token": token,
            "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user