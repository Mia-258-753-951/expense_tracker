
from datetime import date

import pytest

from expense_tracker.domain.models import Expense
from expense_tracker.infrastructure.sqlite_repo import SQLiteExpenseRepository


@pytest.fixture(scope='function')
def repo(tmp_path):
    db_path = tmp_path / 'test.db'
    return SQLiteExpenseRepository(db_path)

def test_add_persitst_in_db_and_get_recovers(repo, tmp_path):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    
    new_id = repo.add(exp1)
    
    repo2 = SQLiteExpenseRepository(tmp_path / 'test.db')
    assert repo2.get(new_id) == exp1
    
def test_add_and_list_all(repo, tmp_path):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    
    repo.add(exp1)
    
    repo2 = SQLiteExpenseRepository(tmp_path / 'test.db')
    assert len(repo2.list_all()) == 1
    
def test_update_persists_changes_and_changes_updated_at(repo, tmp_path):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    
    repo.add(exp1)
    
    exp1.amount = 20000    
    repo.update(exp1)
    
    repo2 = SQLiteExpenseRepository(tmp_path / 'test.db')
    
    updated = repo2.get(exp1.id)
    
    assert updated is not None
    assert updated.amount == 20000
    assert updated.updated_at is not None
    
def test_delete_remove_expense_from_db(repo, tmp_path):
    exp1 = Expense(
        amount=12525,
        date=date(2026, 1, 30),
        category="car",
        wallet="home",
    )
    
    repo.add(exp1)
    
    repo2 = SQLiteExpenseRepository(tmp_path / 'test.db')
    
    recover = repo2.get(exp1.id)
    assert recover is not None
    repo2.delete(recover.id)
    
    deleted = repo2.get(recover.id)
    assert deleted is None
    
def test_init_db_creates_schema_version(repo, tmp_path):    
    with repo._get_connection() as conn:
        row = conn.execute('''
                        SELECT * FROM schema_version
                        ''').fetchone()
        assert row['version'] == 1
    