from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db, get_transaction
from app.models import Category
from app.schemas import CategoryCreate, CategoryResponse

router = APIRouter(
    prefix="/category",
    tags=["Categories"],
)

@router.get("", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    statement = select(Category)
    result= db.execute(statement)
    return result.scalars().all()

@router.post("")
def create_category(category_data: CategoryCreate, db: Session = Depends(get_transaction)):
    category = db.execute(select(Category).where(Category.name == category_data.name)).scalar_one_or_none()
    
    if category:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(name = category_data.name)
    db.add(new_category)
    db.flush()

    return CategoryResponse.model_validate(new_category)