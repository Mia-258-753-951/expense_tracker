
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import date, datetime

from expense_tracker.domain.errors import InvalidAmount, ExpenseDataError

@dataclass
class Expense:
    
    date: date  # 'YYYY-MM-DD'
    amount: int   # En céntimos para evitar floats
    category: str
    wallet: str
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = None
    note: str | None = None
    currency: str = 'EUR'
    id: str = field(default_factory=lambda: uuid4().hex)  # UUID
    
    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise InvalidAmount('"amount" must be > 0.')
        if not isinstance(self.date, date):
            raise ExpenseDataError('"date" must be date object.')
        self.category = (self.category or "").strip()
        if not self.category:
            raise ExpenseDataError('"category" cannot be empty.')
        self.wallet = (self.wallet or '').strip()
        if not self.wallet:
            raise ExpenseDataError('"wallet" cannot be empty.')
        