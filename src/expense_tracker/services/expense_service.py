
from expense_tracker.ports.expense_repo import ExpenseRepository

from expense_tracker.domain.models import Expense

class ExpenseService:
    def __init__(self, repo: ExpenseRepository) -> None:
        self.repo = repo

    def add_expense(self, exp: Expense) -> str:
        return self.repo.add(exp=exp)
    
    def get_expense(self, exp_id: str) -> Expense | None:
        return self.repo.get(exp_id=exp_id)
    
    def list_all_expenses(self) -> list[Expense]:
        return self.repo.list_all()
    
    def list_expenses_by_category(self, category: str) -> list[Expense]:
        return self.repo.list_by_category(category=category)
    
    def list_expenses_by_wallet(self, wallet: str) -> list[Expense]:
        return self.repo.list_by_wallet(wallet=wallet)
    
    def update_expense(self, exp: Expense) -> Expense:
        return self.repo.update(modified_exp= exp)
    
    def delete_expense(self, exp_id: str) -> None:
        self.repo.delete(exp_id=exp_id)
        