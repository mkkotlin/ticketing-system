from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import engine, get_db
from app.schemas import UserCreate, UserResponse, UserRoleUpdate, UserUpdate
from app.models import User
from app.routers import auth
from app.security import hash_password
from app.dependencies import get_current_user, require_role
from app.ticketing import ticket
from app.category import category
from app.enums import UserRole

router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)





@router.get("", response_model=list[UserResponse])
def get(user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    result = db.execute(select(User).order_by(User.id))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}/role", response_model=UserRoleUpdate)
def update_user_role(user_id: int, data: UserRoleUpdate, current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot chnage your own role")

    user.role = data.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    db.delete(user)
    db.commit()














# # Base.metadata.create_all(bind=engine)

# @router.get("/", tags=["Users"])
# def root():
#     return {"message":"Tickering System API"}


# @router.get("/db-test", tags=["Users"])
# def database_test():
#     with engine.connect() as connection:
#         result = connection.execute(text("SELECT 1"))
#         return {"database":result.scalar()}


# @router.post("/users", response_model=UserResponse, tags=["Users"])
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     new_user = User(
#         username=user.username,
#         email=user.email,
#         password_hash=hash_password(user.password)
#     )
#     db.add(new_user)
#     try:
#         db.commit()
#         db.refresh(new_user)
#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=409, detail="Username or email already exists")
#     return new_user


# @router.get("/users", response_model=list[UserResponse], tags=["Users"])
# def get_users(db: Session = Depends(get_db)):
#     statement = select(User)
#     result = db.execute(statement)
#     return result.scalars().all()


# @router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     statement = select(User).where(User.id == user_id)
#     result = db.execute(statement)
#     user = result.scalar_one_or_none()

#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# @router.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
# def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
#     statement = select(User).where(User.id == user_id)
#     result = db.execute(statement)
#     user = result.scalar_one_or_none()

#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user_data.username is not None:
#         user.username = user_data.username

#     if user_data.email is not None:
#         user.email = user_data.email

#     db.commit()
#     db.refresh(user)
#     return user


# @router.delete("/users/{user_id}", tags=["Users"])
# def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("ADMIN"))):
#     statement = select(User).where(User.id == user_id)
#     result = db.execute(statement)

#     user = result.scalar_one_or_none()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}

# # from router.dependencies import require_role
# # @router.get("/admin-test")
# # def admin_test(current_user: User = Depends(require_role("ADMIN"))):
# #     return {"message":"Welcome Admin", "username": current_user.username }

# # @router.get("/agent-test")
# # def agent_test(current_user: User = Depends(require_role("ADMIN", "AGENT"))):
# #     return {"message":"Agent access granted", "username": current_user.username }