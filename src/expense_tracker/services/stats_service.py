from datetime import timedelta
from typing import Any

from expense_tracker.ports.expense_repo import ExpenseRepository
from expense_tracker.services.filters import StatsBy, StatsFilter


class ExpenseStats:
    def __init__(self, repo: ExpenseRepository) -> None:
        self.repo = repo
        
    def month_stats(self, month_year: StatsFilter) -> dict[str, Any]:
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
        
        stats = {}
        stats['total_amount'] = sum(e.amount for e in filtered_exp)
        stats['num_exps'] = len(filtered_exp)
        stats['top_cat'] = sorted(top_cat, key= lambda x: top_cat[x],reverse=True)[:TOP_LIMIT]
        stats['top_wal'] = sorted(top_wal, key= lambda x: top_wal[x],reverse=True)[:TOP_LIMIT]
        
        return stats
    
    def stats_by(self, filter_: StatsFilter) -> Any:
        exps = self.repo.list_all()
        in_range = [e for e in exps if filter_.start_date <= e.date <= filter_.end_date]
        
        if filter_.by is None:
            total = sum(e.amount for e in in_range) * 100
            return (None, {
                'total_amount': total,
                'num_exps': len(in_range),
                'average_exp': total / len(in_range)
            })
        
        stats = {}
        # preparamos por si el fitro es por DAY, que entren todos los días del range elegido
        # creamos un key diario para el range
        current = filter_.start_date
        while current <= filter_.end_date:
            stats[current.isoformat()] = {'total': 0, 'num': 0}
            current += timedelta(days=1)
            
        for e in in_range:
            
            if filter_.by == StatsBy.CATEGORY:
                key = e.category
            if filter_.by == StatsBy.WALLET:
                key = e.wallet
            if filter_.by == StatsBy.DAY:
                key = e.date.isoformat()
            else:
                continue
            # si no es por día (la clave no existía), inicializamos
            if e.category not in stats:
                stats[key] = {'total': 0, 'num': 0}    
            
            stats[key]['total'] += e.amount
            stats[key]['num'] += 1
            
        return (filter_.by.value, stats)
    
    def stats_budget(self, month_year: StatsFilter, limit: float) -> float:
        """
        Recibe el límite de gasto y mes y devuelve el float
        correspondiente al % consumido.
        """
        exps = self.repo.list_all()
        total_spent = (
            sum(e.amount for e in exps 
                if month_year.start_date <= e.date <= month_year.end_date) * 100
        )
        
        return total_spent
                
                    
            
        