from typing import Any

from expense_tracker.domain.models import Expense
from expense_tracker.ports.expense_repo import ExpenseRepository
from expense_tracker.services.filters import ExpenseFilter, ExpenseUpdate, UNSET
from expense_tracker.domain.errors import ExpenseNotFound


class ExpenseService:
    def __init__(self, repo: ExpenseRepository) -> None:
        self.repo = repo

    def add_expense(self, exp: Expense) -> str:
        return self.repo.add(exp=exp)

    def get_expense(self, exp_id: str) -> Expense | None:
        return self.repo.get(exp_id=exp_id)

    def list_expenses(self, filters: ExpenseFilter) -> list[Expense]:
        return self.repo.list_all()

    def update_expense(self, patch: ExpenseUpdate) -> Expense:
        exp = self.repo.get(exp_id=patch.id)        
        if exp is None:
            raise ExpenseNotFound(f'No expense with id "{patch.id}" found.')
        if patch.amount is not None:
            exp.amount = patch.amount
        if patch.category is not None:
            exp.category = patch.category
        if patch.date_ is not None:
            exp.date = patch.date_
        if patch.wallet is not None:
            exp.wallet = patch.wallet
        if patch.currency is not None:
            exp.currency = patch.currency
        if patch.note is not UNSET:
            exp.note = patch.note
            
        return self.repo.update(modified_exp=exp)            

    def delete_expense(self, exp_id: str) -> None:
        self.repo.delete(exp_id=exp_id)
