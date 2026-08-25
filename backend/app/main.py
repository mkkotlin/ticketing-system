from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import engine, Base, get_db
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.models import User
from app.routers import auth
from app.security import hash_password
from app.dependencies import get_current_user, require_role
from app.ticketing import ticket

app = FastAPI(title="Ticketing System")
app.include_router(auth.router)
app.include_router(ticket.router)

# Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message":"Tickering System API"}


@app.get("/db-test")
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database":result.scalar()}


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists")
    return new_user


@app.get("/users", response_model=list[UserResponse], dependencies=[Depends(get_current_user)])
def get_users(db: Session = Depends(get_db)):
    statement = select(User)
    result = db.execute(statement)
    return result.scalars().all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    statement = select(User).where(User.id == user_id)
    result = db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    statement = select(User).where(User.id == user_id)
    result = db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.username is not None:
        user.username = user_data.username

    if user_data.email is not None:
        user.email = user_data.email

    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("ADMIN"))):
    statement = select(User).where(User.id == user_id)
    result = db.execute(statement)

    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# from app.dependencies import require_role
# @app.get("/admin-test")
# def admin_test(current_user: User = Depends(require_role("ADMIN"))):
#     return {"message":"Welcome Admin", "username": current_user.username }

# @app.get("/agent-test")
# def agent_test(current_user: User = Depends(require_role("ADMIN", "AGENT"))):
#     return {"message":"Agent access granted", "username": current_user.username }