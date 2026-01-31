
import pytest
from datetime import date

from expense_tracker.infrastructure.memory_repo import InMemoryExpenseRepository
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.stats_service import ExpenseStats
from expense_tracker.domain.models import Expense
from expense_tracker.services.filters import StatsFilter

@pytest.fixture(scope='function')
def memo_repo():
    return InMemoryExpenseRepository()

@pytest.fixture(scope='function')
def exp_serv(memo_repo):
    return ExpenseService(memo_repo)

@pytest.fixture(scope='function')
def stat_serv(memo_repo):
    return ExpenseStats(memo_repo)


def test_month_stats_returns_dict_with_month_stats(exp_serv, stat_serv):
    
    exp1 = Expense(
        amount=100,
        date=date(2026, 1, 30),
        category='car',
        wallet='home',
    )
    exp2 = Expense(
        amount=100,
        date=date(2026, 1, 30),
        category='car',
        wallet='home',
    )
    
    exp3 = Expense(
        amount=200,
        date=date(2026, 2, 28),
        category='pet',
        wallet='home',
    )
    exp_serv.add_expense(exp1)
    exp_serv.add_expense(exp2)
    exp_serv.add_expense(exp3)
    
    filter_ = StatsFilter(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31)
    )
    
    month_stats = stat_serv.month_stats(filter_)
    
    assert month_stats['total_amount'] == 200
    assert month_stats['num_exps'] == 2
    assert month_stats['top_cat'] == ['car']
    assert month_stats['top_wal'] == ['home']
    
    