from datetime import date

import pytest

from expense_tracker.domain.models import Expense
from expense_tracker.infrastructure.memory_repo import InMemoryExpenseRepository
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.filters import StatsBy, StatsFilter
from expense_tracker.services.stats_service import ExpenseStats


@pytest.fixture(scope="function")
def memo_repo():
    return InMemoryExpenseRepository()


@pytest.fixture(scope="function")
def exp_serv(memo_repo):
    return ExpenseService(memo_repo)


@pytest.fixture(scope="function")
def stat_serv(memo_repo):
    return ExpenseStats(memo_repo)


def test_month_stats_returns_month_info(exp_serv, stat_serv):
    exp1 = Expense(
        amount=100,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    exp2 = Expense(
        amount=100,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )

    exp3 = Expense(
        amount=200,
        date=date(2026, 2, 28),
        category="pet",
        wallet="home",
    )
    exp_serv.add_expense(exp1)
    exp_serv.add_expense(exp2)
    exp_serv.add_expense(exp3)

    filter_ = StatsFilter(start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))

    month_stats = stat_serv.month_stats(filter_)

    assert month_stats.total_amount == 200 / 100
    assert month_stats.count == 2
    assert month_stats.top_categories == ["car"]
    assert month_stats.top_wallets == ["home"]


def test_stats_by_apply_option_and_returns_selected_stats(exp_serv, stat_serv):
    exp1 = Expense(
        amount=100,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    exp2 = Expense(
        amount=100,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )

    exp3 = Expense(
        amount=200,
        date=date(2026, 1, 28),
        category="pet",
        wallet="other",
    )

    exp4 = Expense(
        amount=200,
        date=date(2026, 2, 28),
        category="pet",
        wallet="other",
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

    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 31)

    stats0 = stat_serv.summary_range(start_date, end_date)
    stats1 = stat_serv.by_category(start_date, end_date)
    stats2 = stat_serv.by_wallet(start_date, end_date)
    stats3 = stat_serv.by_day(start_date, end_date)

    assert stats0.total_amount == 4
    assert stats0.count == 3
    assert stats0.average == 4 / 3

    assert isinstance(stats1, list)
    assert len(stats1) == 2
    for s in stats1:
        if s.key == "car":
            assert s.total == 2
            assert s.count == 2
            assert s.percent == s.total / stats0.total_amount * 100
        if s.key == "pet":
            assert s.total == 2
            assert s.count == 1
            assert s.percent == s.total / stats0.total_amount * 100

    assert isinstance(stats2, list)
    assert len(stats2) == 2
    for s in stats2:
        if s.key == "home":
            assert s.total == 2
            assert s.count == 2
            assert s.percent == s.total / stats0.total_amount * 100
        if s.key == "other":
            assert s.total == 2
            assert s.count == 1
            assert s.percent == s.total / stats0.total_amount * 100

    assert isinstance(stats3, list)
    assert len(stats3) == 31
    for s in stats3:
        if s.key == "2026-01-30":
            assert s.total == 2
            assert s.count == 2
            assert s.percent == s.total / stats0.total_amount * 100
        if s.key == "2026-01-28":
            assert s.total == 2
            assert s.count == 1
            assert s.percent == s.total / stats0.total_amount * 100
