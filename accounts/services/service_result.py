from accounts.models import User
from dataclasses import dataclass


@dataclass
class ServiceResult:
    """
    Service Result
    """
    success: bool
    message: str
    user: User | None = None