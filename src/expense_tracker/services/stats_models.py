from dataclasses import dataclass


@dataclass
class StatsSummary:
    total_amount: float
    count: int
    average: float
    top_categories: list[str]
    top_wallets: list[str]
    
@dataclass
class StatsRangeSummary:
    total_amount: float
    count: int
    average: float

@dataclass
class GroupRow:
    key: str
    total: float
    count: int
    percent: float


@dataclass
class BudgetReport:
    year: str
    month: str
    limit: float
    spent: float
    remaining: float
    used: float
    status: str
