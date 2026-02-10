from datetime import date

import pytest

from expense_tracker.domain.models import Expense
from expense_tracker.infrastructure.memory_repo import InMemoryExpenseRepository
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.filters import ExpenseFilter, ExpenseUpdate


@pytest.fixture(scope="function")
def exp_serv():
    memo_repo = InMemoryExpenseRepository()
    service = ExpenseService(memo_repo)
    yield service


def test_add_expense_creates_expense_and_get_expense_reads_it(exp_serv):
    exp = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )

    exp_id = exp_serv.add_expense(exp)
    created = exp_serv.get_expense(exp_id)

    assert exp_id is not None
    assert created is not None
    assert created.wallet == "home"


def test_list_expense_aply_demanded_filters(exp_serv):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )

    exp2 = Expense(
        amount=33333,
        date=date(2026, 2, 28),
        category="pet",
        wallet="home",
    )
    filter_1 = ExpenseFilter(
        start_date=date(2026, 1, 1),
    )
    filter_2 = ExpenseFilter(
        end_date=date(2026, 2, 1),
    )

    filter_3 = ExpenseFilter(category_="car")
    filter_4 = ExpenseFilter(
        wallet_="home",
    )
    filter_5 = ExpenseFilter(
        limit_=2,
    )

    id_1 = exp_serv.add_expense(exp1)
    id_2 = exp_serv.add_expense(exp2)

    added_1 = exp_serv.get_expense(id_1)
    added_2 = exp_serv.get_expense(id_2)

    assert exp_serv.list_expenses(filter_1) == [added_1, added_2]
    assert len(exp_serv.list_expenses(filter_2)) == 1
    assert len(exp_serv.list_expenses(filter_3)) == 1
    assert exp_serv.list_expenses(filter_4) == [added_1, added_2]
    assert exp_serv.list_expenses(filter_5) == [added_1, added_2]


def test_update_expense_returns_patched_expense(exp_serv):
    exp = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )

    exp_id = exp_serv.add_expense(exp)
    created = exp_serv.get_expense(exp_id)

    patch = ExpenseUpdate(id=created.id, amount=22222, date_=date(2026, 2, 1))

    updated = exp_serv.update_expense(patch=patch)

    assert created.id == updated.id
    assert created.note == updated.note
    assert updated.amount == 22222
    assert updated.date == date(2026, 2, 1)

    patch1 = ExpenseUpdate(
        id=created.id,
        note="prueba1",
    )
    filter_1 = ExpenseFilter()

    updated1 = exp_serv.update_expense(patch=patch1)

    assert len(exp_serv.list_expenses(filter_1)) == 1
    assert updated1.note is not None


def test_delete_expenses_deletes_and_returns_none(exp_serv):
    exp = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )

    exp_id = exp_serv.add_expense(exp)

    filter_1 = ExpenseFilter()

    assert len(exp_serv.list_expenses(filter_1)) == 1

    exp_serv.delete_expense(exp_id)

    assert exp_serv.list_expenses(filter_1) == []
