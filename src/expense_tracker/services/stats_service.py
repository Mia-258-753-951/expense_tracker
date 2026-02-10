import calendar
from datetime import date

from expense_tracker.ports.stats_repo import ExpenseStatsRepository

from expense_tracker.services.stats_models import BudgetReport, GroupRow, StatsSummary, StatsRangeSummary


class ExpenseStats:
    def __init__(self, repo: ExpenseStatsRepository) -> None:
        self.repo = repo
        
    def month_stats(self, start_date: date, end_date: date) -> StatsSummary:
        TOP_LIMIT = 3
        if start_date is None or end_date is None:
            raise ValueError("Not a valid date range.")
        
        total, count_ = self.repo.month_summary_stats(start_date, end_date)
        
        top_cat = self.repo.top_categories_by_amount(start_date, end_date, TOP_LIMIT)
        top_wal = self.repo.top_wallets_by_amount(start_date, end_date, TOP_LIMIT)
                
        return StatsSummary(
            total_amount=total/100,
            count=count_,
            average= (total/100) / count_ if count_ else 0,
            top_categories=[cat for cat, _ in top_cat],
            top_wallets=[wal for wal, _ in top_wal],
        )

    def summary_range(self, start_date: date, end_date: date) -> StatsRangeSummary:
        if end_date < start_date:
            raise ValueError('"end_date" must be >= "start_date".')
        
        total, count = self.repo.summary_range_stats(start_date, end_date)

        return StatsRangeSummary(
            total_amount=total/100,
            count=count,
            average=(total/100) / count if count else 0,
        )

    def by_category(self, start_date: date, end_date: date) -> list[GroupRow]:
        results = self.repo.by_category_stats(start_date, end_date)
        total = sum(r[2] for r in results)
        by_cat=[]
        for k, c, t in results:
            g = GroupRow(
                key=k,
                total=t/100,
                count=c,
                percent=(t/total) * 100 if total else 0,
            )
            by_cat.append(g)
        return by_cat

    def by_wallet(self, start_date: date, end_date: date) -> list[GroupRow]:
        results = self.repo.by_wallet_stats(start_date, end_date)
        total = sum(r[2] for r in results)
        by_wal=[]
        for k, c, t in results:
            g = GroupRow(
                key=k,
                total=t/100,
                count=c,
                percent=(t/total) * 100 if total else 0,
            )
            by_wal.append(g)
        return by_wal

    def by_day(self, start_date: date, end_date: date) -> list[GroupRow]:
        results = self.repo.by_category_stats(start_date, end_date)
        total = sum(r[2] for r in results)
        by_day=[]
        for k, c, t in results:
            g = GroupRow(
                key=k,
                total=t/100,
                count=c,
                percent=(t/total) * 100 if total else 0,
            )
            by_day.append(g)
        return by_day

    def budget_month(self, year: str, month: str, limit: float, warn_at: int) -> BudgetReport:
        start_date = date(int(year), int(month), 1)
        last_day = calendar.monthrange(start_date.year, start_date.month)[
            1
        ]  # [0] devuelve día semana que empieza [1] total días del mes
        end_date = start_date.replace(day=last_day)

        total, _ = self.repo.summary_range_stats(start_date, end_date)
        
        if total / 100 < warn_at / 100 * limit:
            status = "OK"
        elif total / 100 < limit:
            status = "WARNING"
        else:
            status = "EXCEEDED"

        return BudgetReport(
            year=year,
            month=month,
            limit=limit,
            spent=total / 100,
            remaining=limit - total/100,
            used=((total/100) / limit) * 100,  # lo devolvemos en porcentaje
            status=status,
        )
