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

@router.get("", response_model=list[TicketResponse])
def get_tickets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    statement = select(Ticket)
    if current_user.role == "CUSTOMER":
        statement = statement.where(Ticket.created_by_id == current_user.id)
    elif current_user.role == "AGENT":
        statement = statement.where(Ticket.assigned_to_id == current_user.id)
    elif current_user.role == "ADMIN":
        pass
    result = db.execute(statement)
    return result.scalars().all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    statement = select(Ticket).where(Ticket.id == ticket_id)
    ticket = db.execute(statement).scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == "CUSTOMER":
        if ticket.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have access to this ticket")
    elif current_user.role == "AGENT":
        if ticket.assigned_to_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have access to this ticket")
    return ticket


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
