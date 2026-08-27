from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..enums import TicketStatus, UserRole
from ..models import Ticket, User
from ..schemas import TicketUpdate

class TicketService:
    @staticmethod
    def update_ticket(db: Session, ticket: Ticket, current_user: User, data:TicketUpdate) -> Ticket:
        if current_user.role == UserRole.CUSTOMER:
            raise HTTPException(status_code=403, detail="Customers cannot update tickets")

        # --------------------------AGENT-------------------------
        if current_user.role == UserRole.AGENT:
            if ticket.assigned_to_id != current_user.id:
                raise HTTPException(status_code=403, detail="You can only update tickets assigned to you")

            if data.assigned_to_id is not None:
                raise HTTPException(status_code=403, detail="Agents cannot reassign tickets")

            if data.priority is not None:
                raise HTTPException(status_code=403, detail="Agents cannot change ticket priority")

            if data.status is not None:
                TicketService._update_status(ticket, data.status)

        # -----------------------ADMIN----------------------------
        elif current_user.role == UserRole.ADMIN:
            if data.status is not None:
                TicketService._update_status(ticket, data.status)

            if data.priority is not None:
                ticket.priority = data.priority

            if data.assigned_to_id is not None:
                agent = db.execute(select(User).where(User.id == data.assigned_to_id)).scalar_one_or_none()

                if agent is None:
                    raise HTTPException(status_code=404, detail="User not found")

                if agent.role != UserRole.AGENT:
                    raise HTTPException(status_code=400, detail="Ticket can only be assigned to an agent")

                ticket.assigned_to_id = agent.id
        ticket.updated_at = datetime.now()

    @staticmethod
    def _update_status(ticket: Ticket, new_status: TicketStatus):
        allowed_tansactions = {
            TicketStatus.OPEN:{ TicketStatus.IN_PROGRESS},
            TicketStatus.IN_PROGRESS: {TicketStatus.WAITING_FOR_CUSTOMER, TicketStatus.RESOLVED},
            TicketStatus.WAITING_FOR_CUSTOMER:{TicketStatus.IN_PROGRESS},
            TicketStatus.RESOLVED:{TicketStatus.CLOSED, TicketStatus.IN_PROGRESS},
            TicketStatus.CLOSED: set()
        }
        current_status = ticket.status
        if new_status == current_status:
            return

        if new_status not in allowed_tansactions[current_status]:
            raise HTTPException(status_code=400, detail=(f"Invalid status transation: " f"{current_status} -> {new_status}"))

        ticket.status = new_status
        if new_status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now()
        elif new_status != TicketStatus.RESOLVED:
            ticket.resolved_at = None

    @staticmethod
    def assign_ticket(db: Session, ticket: Ticket, agent_id: int) -> Ticket:
        agent = db.execute(select(User).where(User.id == agent_id)).scalar_one_or_none()

        if agent is None:
            raise HTTPException(status_code=404, detail="User not found")

        if agent.role != UserRole.AGENT:
            raise HTTPException(status_code=400, detail="Ticket can only be assigned to an agent")

        ticket.assigned_to_id = agent.id
        ticket.updated_at = datetime.now()
        return ticket


    @staticmethod
    def unassign_ticket(ticket: Ticket) -> Ticket:
        ticket.assigned_to_id = None
        ticket.updated_at = datetime.now()
        return ticket