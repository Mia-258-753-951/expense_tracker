from datetime import datetime

from expense_tracker.domain.errors import ExpenseAlreadyExists, ExpenseNotFound
from expense_tracker.domain.models import Expense
from expense_tracker.ports.expense_repo import ExpenseRepository


class InMemoryExpenseRepository(ExpenseRepository):
    def __init__(self) -> None:
        self._data: dict[str, Expense] = {}

    def add(self, exp: Expense) -> str:
        if exp.id in self._data:
            raise ExpenseAlreadyExists(f'Expense with id "{exp.id}" already exists.')
        self._data[exp.id] = exp
        return exp.id

    def get(self, exp_id: str) -> Expense | None:
        if exp_id not in self._data:
            raise ExpenseNotFound(f'No expense with id "{exp_id}" found.')
        return self._data.get(exp_id)

    def list_all(self) -> list[Expense]:
        return [e for e in self._data.values()]

    def update(self, modified_exp: Expense) -> Expense:
        modified_exp.updated_at = datetime.now()
        self._data[modified_exp.id] = modified_exp
        return modified_exp

    def delete(self, exp_id: str) -> None:
        if exp_id not in self._data:
            raise ExpenseNotFound(f'No expense with id "{exp_id}" found.')
        del self._data[exp_id]
        return None
