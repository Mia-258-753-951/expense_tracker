import pytest
from datetime import date

from expense_tracker.infrastructure.json_repo import JsonExpenseRepository
from expense_tracker.domain.models import Expense


@pytest.fixture(scope='function')
def repo(tmp_path):
    path = tmp_path / 'test.json'
    yield JsonExpenseRepository(path)

def test_add_create_json_file_and_list_all_contains_added(repo, tmp_path):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    
    repo.add(exp1)
    
    assert repo.path.exists()    
    assert len(repo.list_all() ) == 1
    
    repo2 = JsonExpenseRepository(tmp_path / 'test.json')
    assert len(repo2.list_all()) == 1
    
def test_update_persists_updated_at_and_persists_changes(repo):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    
    repo.add(exp1)
    exp1.category = 'veterinary'    
    assert exp1.updated_at == None
    
    repo.update(exp1)    
    updated = repo.get(exp1.id)
    assert updated.category == 'veterinary'
    assert updated.updated_at is not None
    
        
def test_delete_persist_and_erase_record(repo, tmp_path):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    
    repo.add(exp1)
    
    assert exp1.id in repo.data
    repo.delete(exp1.id)
    assert exp1.id not in repo.data
    
    repo2 = JsonExpenseRepository(tmp_path / 'test.json')
    assert len(repo2.list_all()) == 0
    