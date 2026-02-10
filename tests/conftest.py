
from fastapi.testclient import TestClient
import pytest

from expense_tracker.api.deps import get_expense_service, get_stats_service
from expense_tracker.infrastructure.sqlite_repo import SQLiteExpenseRepository
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.stats_service import ExpenseStats
from expense_tracker.api.app import app

@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / 'test.db'
    repo = SQLiteExpenseRepository(db_path)
    
    def override_get_expense_service():
        return ExpenseService(repo)
    def override_get_stats_service():
        return ExpenseStats(repo)

    app.dependency_overrides[get_expense_service] = override_get_expense_service
    app.dependency_overrides[get_stats_service] = override_get_stats_service

    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()
        
