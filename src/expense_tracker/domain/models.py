from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import uuid4

from expense_tracker.domain.errors import ExpenseDataError, InvalidAmount


@dataclass
class Expense:
    date: date  # 'YYYY-MM-DD'
    amount: int  # En céntimos para evitar floats
    category: str
    wallet: str
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = None
    note: str | None = None
    currency: str = "EUR"
    id: str = field(default_factory=lambda: uuid4().hex)  # UUID

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise InvalidAmount('"amount" must be > 0.')
        if not isinstance(self.date, date):
            raise ExpenseDataError('"date" must be date object.')
        self.category = (self.category or "").strip()
        if not self.category:
            raise ExpenseDataError('"category" cannot be empty.')
        self.wallet = (self.wallet or "").strip()
        if not self.wallet:
            raise ExpenseDataError('"wallet" cannot be empty.')
    
    def __str__(self) -> str:
    # Convertimos céntimos a formato decimal (p.e. 1050 -> 10,50)
        amount_fmt = f"{self.amount / 100:,.2f} {self.currency}"
        date_fmt = self.date.strftime("%d/%m/%Y")
        
        return (
            f"[{date_fmt}] {self.category:<12} | "
            f"{amount_fmt:>10} | "
            f"Wallet: {self.wallet} "
            f"{'(' + self.note + ')' if self.note else ''}"
        )
