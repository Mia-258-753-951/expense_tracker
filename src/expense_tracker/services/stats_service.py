from datetime import timedelta, date
import calendar

from expense_tracker.ports.expense_repo import ExpenseRepository
from expense_tracker.services.filters import StatsFilter
from expense_tracker.services.stats_models import StatsSummary, GroupRow, BudgetReport


class ExpenseStats:
    def __init__(self, repo: ExpenseRepository) -> None:
        self.repo = repo
        
    def month_stats(self, month_year: StatsFilter) -> StatsSummary:
        TOP_LIMIT = 3
        exps = self.repo.list_all()
        if month_year.start_date is None or month_year.end_date is None:
            raise ValueError('Not a valid date range.')
        
        filtered_exp = [e for e in exps if month_year.start_date<= e.date <= month_year.end_date]
        top_cat = {}
        top_wal = {}
        for e in filtered_exp:
            # Separados en dos dicts por si alguna categoría se llamara igual que una wallet.
            top_cat[e.category] = top_cat.get(e.category, 0) + e.amount
            top_wal[e.wallet] = top_wal.get(e.wallet, 0) + e.amount     
        
                        
        return StatsSummary(
            total_amount=sum(e.amount for e in filtered_exp)/100,
            count=len(filtered_exp),
            average = (sum(e.amount for e in filtered_exp)/100)/len(filtered_exp) if len(filtered_exp) != 0 else 0,
            top_categories=sorted(top_cat, key= lambda x: top_cat[x],reverse=True)[:TOP_LIMIT],
            top_wallets=sorted(top_wal, key= lambda x: top_wal[x],reverse=True)[:TOP_LIMIT],
        )
        
        
    def summary_range(self, start_date: date, end_date: date) -> StatsSummary:
        exps = self.repo.list_all()
        in_range = [e for e in exps if start_date <= e.date <= end_date]
        
        total = sum(e.amount for e in in_range) / 100  # dividimos entre 100 para que el CLI recibas Euros, no céntimos
        
        return StatsSummary(
                total_amount= total,
                count=len(in_range),
                average=total/len(in_range) if in_range else 0,
            )
    
    def by_category(self, start_date: date, end_date: date) -> list[GroupRow]:
        exps = self.repo.list_all()
        in_range = [e for e in exps if start_date <= e.date <= end_date]
        total = sum(e.amount for e in in_range) 
        stats = {}
        for e in in_range:
            if e.category not in stats:
                stats[e.category] = {'total_amount': 0, 'count': 0}
            stats[e.category]['total_amount'] += e.amount
            stats[e.category]['count'] += 1
        by_cat = []
        for k in stats:
            g = GroupRow(
                key=k,
                total=stats[k]['total_amount']/100,
                count=stats[k]['count'],
                percent=(stats[k]['total_amount']/total)*100 if total else 0
            )
            by_cat.append(g)
        return by_cat
    
    def by_wallet(self, start_date: date, end_date: date) -> list[GroupRow]:
        exps = self.repo.list_all()
        in_range = [e for e in exps if start_date <= e.date <= end_date]
        total = sum(e.amount for e in in_range) 
        stats = {}
        for e in in_range:
            if e.wallet not in stats:
                stats[e.wallet] = {'total_amount': 0, 'count': 0}
            stats[e.wallet]['total_amount'] += e.amount
            stats[e.wallet]['count'] += 1
        by_wal = []
        for k in stats:
            g = GroupRow(
                key=k,
                total=stats[k]['total_amount']/100,
                count=stats[k]['count'],
                percent=(stats[k]['total_amount']/total)*100 if total else 0
            )
            by_wal.append(g)
        return by_wal
    
    def by_day(self, start_date: date, end_date: date) -> list[GroupRow]:
        exps = self.repo.list_all()
        in_range = [e for e in exps if start_date <= e.date <= end_date]
        total = sum(e.amount for e in in_range)
        
        current = start_date
        stats = {}
        # generamos una key por día del rango, incluyendo los que no tengan expense definido
        while current <= end_date:
            stats[current.isoformat()] = {'total_amount': 0, 'count': 0}
            current += timedelta(days=1)
        
        for e in in_range:
            stats[e.date.isoformat()]['total_amount'] += e.amount
            stats[e.date.isoformat()]['count'] += 1
        
        by_day = []
        for k in stats:
            g = GroupRow(
                key=k,
                total=stats[k]['total_amount']/100,
                count=stats[k]['count'],
                percent=(stats[k]['total_amount']/total)*100 if total else 0
            )
            by_day.append(g)
        return by_day
            
                
    def budget_month(self, year: str, month: str, limit: float, warn_at: int) -> BudgetReport:
        start_date = date(int(year), int(month), 1)
        last_day = calendar.monthrange(start_date.year, start_date.month)[1]  # [0] devuelve día semana que empieza [1] total días del mes
        end_date = start_date.replace(day=last_day)
        
        exps = self.repo.list_all()
        in_range = [e for e in exps if start_date <= e.date <= end_date]
        total_spent=sum(e.amount for e in in_range) / 100
        
        if  total_spent < warn_at/100 * limit:
            status = 'OK'
        elif total_spent < limit:
            status = 'WARNING'
        else:
            status = 'EXCEEDED'
            
        return BudgetReport(
            year=year,
            month=month,
            limit=limit,
            spent=total_spent,
            remaining=limit-total_spent,
            used=total_spent/limit,
            status=status,
        )