from expense_tracker.domain.errors import ExpenseNotFound
from expense_tracker.domain.models import Expense
from expense_tracker.ports.expense_repo import ExpenseRepository
from expense_tracker.services.filters import UNSET, ExpenseFilter, ExpenseUpdate


class ExpenseService:
    def __init__(self, repo: ExpenseRepository) -> None:
        self.repo = repo

    def add_expense(self, exp: Expense) -> str:
        new_exp = self.repo.get(exp.id)
        if new_exp is not None:
            raise KeyError(f'Expense with id "{exp.id}" already exists.')
        return self.repo.add(exp=exp)

    def get_expense(self, exp_id: str) -> Expense | None:
        return self.repo.get(exp_id=exp_id)

    def list_expenses(self, filters: ExpenseFilter) -> list[Expense]:
        exps = self.repo.list_all()

        if filters.from_date_ is not None:
            exps = [e for e in exps if e.date >= filters.from_date_]
        if filters.to_date_ is not None:
            exps = [e for e in exps if e.date <= filters.to_date_]
        if filters.category_ is not None:
            exps = [
                e for e in exps if e.category.casefold() == filters.category_.strip().casefold()
            ]
        if filters.wallet_ is not None:
            exps = [e for e in exps if e.wallet.casefold() == filters.wallet_.strip().casefold()]
        if filters.limit_ is not None:
            exps = [e for e in exps][: filters.limit_]
        if filters.sort_ is not None:
            if filters.sort_ == "amount":
                exps = sorted(exps, key=lambda e: e.amount)
            if filters.sort_ == "date":
                exps = sorted(exps, key=lambda e: e.date)

        return exps

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
        exp = self.repo.get(exp_id=exp_id)
        if exp is None:
            raise ExpenseNotFound(f'No expense with id "{exp_id}" found.')
        self.repo.delete(exp_id=exp_id)
