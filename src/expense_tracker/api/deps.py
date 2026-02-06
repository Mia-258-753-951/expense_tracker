
from functools import lru_cache
from pathlib import Path

from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.infrastructure.sqlite_repo import SQLiteExpenseRepository
from expense_tracker.services.stats_service import ExpenseStats


DB_PATH = Path('data/expenses.db')

# con @lru_cache la primera ejecución guarda resultado en caché y luego siempre obtenemos este resultado(mismo repo cada vez)
# la primera ejecuta init_db() (crea o valida schema). Resto de llamadas no ejecuta esto.
@lru_cache
def get_repo():
    return SQLiteExpenseRepository(DB_PATH)

def get_expense_service():
    return ExpenseService(get_repo())

def get_stats_service():
    return ExpenseStats(get_repo())

