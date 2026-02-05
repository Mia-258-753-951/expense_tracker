
from pathlib import Path
import sqlite3
from datetime import datetime, date


from expense_tracker.ports.expense_repo import ExpenseRepository
from expense_tracker.ports.stats_repo import ExpenseStatsRepository
from expense_tracker.domain.models import Expense
from expense_tracker.infrastructure.db import DB_PATH, init_db

class SQLiteExpenseRepository(ExpenseRepository, ExpenseStatsRepository):
    
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path
        init_db(self.path)        
    
    # helper para abrir conexión específica para cada transacción. cursor se crea in-situ
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn
    
    # helper de mapeo row -> domain
    def _row_to_model(self, row: sqlite3.Row) -> Expense:
        # convertimos el objeto Row (inmutable) a un dict real (manipulable)
        data = dict(row)
        data['date'] = date.fromisoformat(data['date'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(
            data['updated_at']
            ) if data['updated_at'] is not None else None
        
        return Expense(**data)
    
    def add(self, exp: Expense) -> str:
        stmt = '''
        INSERT INTO expenses (id, date, amount, category, wallet, note, currency, created_at, updated_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        values = (
            exp.id,
            exp.date.isoformat(),
            exp.amount,
            exp.category,
            exp.wallet,
            exp.note,
            exp.currency,
            exp.created_at.isoformat(),
            exp.updated_at.isoformat() if exp.updated_at is not None else None,
        )
        
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(stmt, values)
                                
        return exp.id        

    def get(self, exp_id: str) -> Expense | None:
        stmt = '''
        SELECT * FROM expenses
        WHERE id=?
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()
            row = cur.execute(stmt, (exp_id,)).fetchone()
        
        if row is None:
            return None
        return self._row_to_model(row)            

    def list_all(self) -> list[Expense]:
        stmt = '''
        SELECT * FROM expenses
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()
            rows = cur.execute(stmt).fetchall()
        
        return [self._row_to_model(row) for row in rows]

    def update(self, modified_exp: Expense) -> Expense:
        modified_exp.updated_at = datetime.now()
        
        stmt = '''
        UPDATE expenses SET
            date=?,
            amount=?,
            category=?,
            wallet=?,
            note=?,
            currency=?,
            updated_at=?
        WHERE id=?            
            '''
        values = (
            modified_exp.date.isoformat(),
            modified_exp.amount,
            modified_exp.category,
            modified_exp.wallet,
            modified_exp.note,
            modified_exp.currency,
            modified_exp.updated_at.isoformat(),
            modified_exp.id,
        )
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(stmt, values)
        
        return modified_exp

    def delete(self, exp_id: str) -> None:
        stmt = '''
        DELETE FROM expenses
        WHERE id=?
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(stmt, (exp_id,))
        
        return None

    # métodos de STATS
    
    def month_summary_stats(self, start_date: date, end_date: date) -> tuple[int, int]:
        stmt = '''
        SELECT COALESCE(SUM(amount), 0), COUNT(*)
        FROM expenses
        WHERE date BETWEEN ? AND ?
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()            
            row = cur.execute(stmt, (start_date, end_date,)).fetchone()
        
        return row
    
    def top_categories_by_amount(self, start_date: date, end_date: date, limit: int) -> list[tuple[str, int]]:
        stmt = '''
        SELECT category, SUM(amount) FROM expenses
        WHERE date BETWEEN ? AND ?
        GROUP BY category 
        ORDER BY SUM(amount) DESC
        LIMIT ?        
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()            
            row = cur.execute(stmt, (start_date, end_date, limit,)).fetchall()
        
        return row
    
    def top_wallets_by_amount(self, start_date: date, end_date: date, limit: int) -> list[tuple[str, int]]:
        stmt = '''
        SELECT wallet, SUM(amount) FROM expenses
        WHERE date BETWEEN ? AND ?
        GROUP BY wallet 
        ORDER BY SUM(amount) DESC
        LIMIT ?        
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()            
            row = cur.execute(stmt, (start_date, end_date, limit,)).fetchall()
        
        return row

    def summary_range_stats(self, start_date: date, end_date: date) -> tuple[int, int]:
        stmt = '''
        SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expenses
        WHERE date BETWEEN ? AND ?
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()            
            row = cur.execute(stmt, (start_date, end_date,)).fetchone()
        
        return row
    
    def by_category_stats(self, start_date: date, end_date: date) -> list[tuple[str, int, int]]:
        stmt = '''
        SELECT category, COUNT(*), SUM(amount) FROM expenses
        WHERE date BETWEEN ? and ? 
        GROUP BY category 
        ORDER BY date DESC
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()            
            rows = cur.execute(stmt, (start_date, end_date,)).fetchall()
        
        return [(r[0], r[1], r[2]) for r in rows]
    
    def by_wallet_stats(self, start_date: date, end_date: date) -> list[tuple[str, int, int]]:
        stmt = '''
        SELECT wallet, COUNT(*), SUM(amount) FROM expenses
        WHERE date BETWEEN ? and ? 
        GROUP BY wallet 
        ORDER BY SUM(amount) DESC
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()            
            rows = cur.execute(stmt, (start_date, end_date,)).fetchall()
        
        return [(r[0], r[1], r[2]) for r in rows]
    
    def by_day_stats(self, start_date: date, end_date: date) -> list[tuple[str, int, int]]:
        stmt = '''
        SELECT date, COUNT(*), SUM(amount) FROM expenses
        WHERE date BETWEEN ? and ? 
        GROUP BY date 
        ORDER BY SUM(amount) DESC
        '''
        with self._get_connection() as conn:
            cur = conn.cursor()            
            rows = cur.execute(stmt, (start_date, end_date,)).fetchall()
        
        return [(r[0], r[1], r[2]) for r in rows]
    
