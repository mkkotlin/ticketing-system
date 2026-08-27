from sqlalchemy.orm import Session
from ..models import TicketActivity


class ActivityService:
    @staticmethod
    def log(db: Session, ticket_id: int, user_id: int, action: str, old_value: str | None = None, new_value: str | None = None):
        activity = TicketActivity(ticket_id=ticket_id,
                                  user_id=user_id, action=action, old_value=old_value, new_value=new_value)

        db.add(activity)
        return activity