
from dataclasses import dataclass

@dataclass
class StatsSumary:
    total_amount: float
    count: int
    average: float
    top_categories: list[str] | None = None
    top_wallets: list[str] | None = None
    
@dataclass
class GroupRow:
    key: str
    total: float
    count: int
    percent: float