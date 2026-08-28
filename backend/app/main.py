from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import engine, get_db
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.models import User
from app.routers import auth
from app.security import hash_password
from app.dependencies import get_current_user, require_role
from app.ticketing import ticket
from app.category import category
from app.Users import users
from app.comments import comments
from app.activities import activities
from app.exceptions import AppException
from app.exception_handlers import app_exception_handler, unexpected_exception_handler




app = FastAPI(title="Ticketing System", version="1.0.0")


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)

@app.get("/")
def root():
    return {"message": "Ticketing System API"}
app.include_router(activities.router)
app.include_router(auth.router)
app.include_router(category.router)
app.include_router(comments.router)
app.include_router(ticket.router)
app.include_router(users.router)

