from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Ticket, User
from app.schemas import TicketResponse, TicketCreate
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
    # dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=list[TicketResponse])
def get_tickets(db: Session = Depends(get_db)):
    s = select(Ticket)
    res = db.execute(s)
    return res.scalars().all()

@router.post("/", response_model=TicketResponse)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    category = db.execute(select(Category).where(Category.id == ticket_data.category_id)).scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="category not found")
    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        category_id=ticket_data.category_id,
        priority=ticket_data.priority,
        created_by_id=current_user.id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket
