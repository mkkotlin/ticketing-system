class AppException(Exception):
    def __init__(self, error: str, message: str, status_code: int):
        self.error = error
        self.message = message
        self.status_code = status_code


class TicketNotFound(AppException):
    def __init__(self):
        super().__init__(error="TICKET_NOT_FOUND", message="Ticket not found", status_code=404)


class UserNotFound(AppException):
    def __init__(self):
        super().__init__(error="USER_NOT_FOUND", message="User not found", status_code=404)

class ForbiddenAction(AppException):
    def __init__(self, message="You do not have permission"):
        super().__init__(error="FORBIDDEN", message=message, status_code=403)


class InvalidStatusTransition(AppException):
    def __init__(self, old_status: str, new_status: str):
        super().__init__(error="INVALID_STATUS_TRANSITION", message=(f"Invalid status transition: " f"{old_status} \u2192 {new_status}"), status_code=400)


class AccountInactive(AppException):
    def __init__(self, message="User account is inactive"):
        super().__init__(error="ACCOUNT_INACTIVE", message=message, status_code=403)