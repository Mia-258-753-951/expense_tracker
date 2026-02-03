
import pytest
from datetime import date

from expense_tracker.infrastructure.memory_repo import InMemoryExpenseRepository
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.stats_service import ExpenseStats
from expense_tracker.domain.models import Expense
from expense_tracker.services.filters import StatsFilter, StatsBy

@pytest.fixture(scope='function')
def memo_repo():
    return InMemoryExpenseRepository()

@pytest.fixture(scope='function')
def exp_serv(memo_repo):
    return ExpenseService(memo_repo)

@pytest.fixture(scope='function')
def stat_serv(memo_repo):
    return ExpenseStats(memo_repo)


def test_month_stats_returns_month_info(exp_serv, stat_serv):
    
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
    
    assert month_stats.total_amount == 20000
    assert month_stats.count == 2
    assert month_stats.top_categories == ['car']
    assert month_stats.top_wallets == ['home']
    
def test_stats_by_apply_option_and_returns_selected_stats(exp_serv, stat_serv):
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
        date=date(2026, 1, 28),
        category='pet',
        wallet='other',
    )
    
    exp4 = Expense(
        amount=200,
        date=date(2026, 2, 28),
        category='pet',
        wallet='other',
    )
    exp_serv.add_expense(exp1)
    exp_serv.add_expense(exp2)
    exp_serv.add_expense(exp3)
    exp_serv.add_expense(exp4)
    
    _filter0 = StatsFilter(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        by=None,
    )
    
    _filter1 = StatsFilter(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        by=StatsBy.CATEGORY,
    )
    
    _filter2 = StatsFilter(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        by=StatsBy.WALLET,
    )
    
    _filter3 = StatsFilter(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        by=StatsBy.DAY,
    )
    
    key0, stats0 = stat_serv.stats_by(filter_=_filter0)
    key1, stats1 = stat_serv.stats_by(filter_=_filter1)
    key2, stats2 = stat_serv.stats_by(filter_=_filter2)
    key3, stats3 = stat_serv.stats_by(filter_=_filter3)
    
    assert key0 == None
    assert stats0.total_amount == 4
    assert stats0.count == 3
    assert stats0.average == 4/3
    
    assert key1 == 'category'
    assert isinstance(stats1, list)
    assert len(stats1) == 31
    for s in stats1:
        if s.key == 'car':
            assert s.total == 2
            assert s.count == 2
            assert s.percent == 2 / 2
        if s.key == 'wallet':
            assert s.total == 2
            assert s.count == 1
            assert s.percent == 2 / 1
            
    assert key2 == 'wallet'
    assert isinstance(stats2, list)
    assert len(stats2) == 31
    for s in stats2:
        if s.key == 'home':
            assert s.total == 2
            assert s.count == 2
            assert s.percent == 2 / 2
        if s.key == 'pet':
            assert s.total == 2
            assert s.count == 1
            assert s.percent == 2 / 1
            
    assert key3 == 'day'
    assert isinstance(stats3, list)
    assert len(stats3) == 31
    for s in stats3:
        if s.key == '2026-01-30':
            assert s.total == 2
            assert s.count == 2
            assert s.percent == 2 / 2
        if s.key == '2026-01-28':
            assert s.total == 2
            assert s.count == 1
            assert s.percent == 2 / 1
        
    