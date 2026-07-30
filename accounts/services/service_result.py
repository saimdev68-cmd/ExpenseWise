from dataclasses import dataclass
from accounts.models import User


@dataclass
class ServiceResult:
    success: bool
    message: str
    user: User | None = None