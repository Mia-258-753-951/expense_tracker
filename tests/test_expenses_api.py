
from helpers import seed_expenses

def test_health_main(client):
    
    r = client.get('/health')
    
    assert r.status_code == 200
    
def test_health_expenses(client):
    
    r = client.get('/expenses/health')
    
    assert r.status_code == 200
    
def test_health_stats(client):
    
    r = client.get('/stats/health')
    
    assert r.status_code == 200
    
def test_create_expense_returns_id(client):
    
    payload = {
        "amount": 400,
        "date": "2026-02-01",
        "category": "pet",
        "wallet": "home",
        "note": "nota 1",
    }
    
    r = client.post('/expenses', json=payload)
    
    data = r.json()    
    assert r.status_code == 201
    assert 'id' in data
    assert isinstance(data['id'], str)
    assert data['id'] != ''
    
def test_get_expenses_initially_empty(client):
    r = client.get('/expenses')
    
    assert r.status_code == 200
    assert r.json() == []
    
def test_create_expense_get_eur_currency_by_default(client):
    payload = {
        "amount": 400,
        "date": "2026-02-01",
        "category": "pet",
        "wallet": "home",
        "note": "nota 1",
    }
    
    client.post('/expenses', json=payload)
    r = client.get('/expenses')
    assert r.status_code == 200
    
    items = r.json()
    assert items[0]['currency'] == 'EUR'
    
    
    
def test_get_expenses_after_create_returns_one(client):
    
    payload = {
        "amount": 400,
        "date": "2026-02-01",
        "category": "pet",
        "wallet": "home",
        "note": "nota 1",
    }
    
    client.post('/expenses', json=payload)    
    r = client.get('/expenses')
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]['category'] == 'pet'
    assert items[0]["wallet"] == "home"
    assert items[0]["amount"] == 400.0
    
def test_get_expenses_apply_category_filter(client):
    seed_expenses(client)
    r = client.get('/expenses')
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    
    r = client.get('/expenses', params={'category': 'pet'})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    assert sum(i['amount'] for i in items) == 800.0
    

def test_get_expenses_apply_wallet_filter(client):
    seed_expenses(client)
    r = client.get('/expenses')
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    
    r = client.get('/expenses', params={'wallet': 'home'})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    assert sum(i['amount'] for i in items) == 1100.0
    
def test_get_expenses_apply_from_to_filter(client):
    seed_expenses(client)
    r = client.get('/expenses')
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    
    r = client.get('/expenses', params={'from_': '2026-02-01', 'to': '2026-02-28'})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    amounts = sorted(i["amount"] for i in items)
    assert amounts == [400.0, 700.0]
    
def test_get_expenses_apply_limit_filter(client):
    seed_expenses(client)
    r = client.get('/expenses')
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    
    r = client.get('/expenses', params={'limit': 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]['amount'] == 400.0
    
def test_get_expenses_apply_sort_filter(client):
    seed_expenses(client)
    r = client.get('/expenses')
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    amounts = [i["amount"] for i in items]
    assert sorted(amounts) == [400.0, 400.0, 700.0]
    
    r = client.get('/expenses', params={'sort': 'amount'})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    assert items[0]['amount'] == 400.0
    assert items[1]['amount'] == 400.0
    assert items[2]['amount'] == 700.0
    
    r = client.get('/expenses', params={'sort': 'date'})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    dates = [i["date"] for i in items]
    assert dates == ["2026-02-01", "2026-02-15", "2026-03-01"]
    
def test_get_by_id_returns_propper_expense(client):
    ids = seed_expenses(client)
    
    r = client.get(f'/expenses/{ids[0]}')
    data = r.json()
    
    assert r.status_code == 200, r.text
    
    assert data['amount'] == 400.0
    assert data['date'] == '2026-02-01'
    assert data['category'] == 'pet'
    assert data['wallet'] == 'home'

def test_get_by_id_raise_if_invalid_id(client):
    
    r = client.get('/expenses/1234')
    assert r.status_code == 404, r.text
    
def test_delete_returns_204_status_if_ok(client):
    ids = seed_expenses(client)
    
    # comprobamos existencia previa
    r = client.get(f'/expenses/{ids[0]}')
    data = r.json()    
    assert r.status_code == 200, r.text    
    assert data['amount'] == 400.0
    
    # borrado
    r = client.delete(f'/expenses/{ids[0]}')
    assert r.status_code == 204, r.text
    
    # comprobamos no existencia tras borrado
    r = client.get(f'/expenses/{ids[0]}')
    assert r.status_code == 404, r.text    
    
def test_delete_raise_if_invalid_id(client):
    r = client.delete('/expenses/1234')
    assert r.status_code == 404, r.text
    
def test_patch_update_required_fields_returns_patched_expense_and_persists_updated_at(client):
    ids = seed_expenses(client)
    
    # comprobamos campo antes de cambio
    r = client.get(f'/expenses/{ids[0]}')
    data = r.json()    
    assert r.status_code == 200, r.text    
    assert data['amount'] == 400.0
    assert data['date'] == "2026-02-01"
    
    # pasamos patch
    r = client.patch(f'/expenses/{ids[0]}', json={'amount': 500, 'date_': "2026-04-01"})
    assert r.status_code == 200, r.text
    data = r.json() 
    assert data['amount'] == 500.0
    assert data['date'] == "2026-04-01"
    assert data['id'] == ids[0]
    assert data['updated_at'] is not None
    
    # comprobamos persistencia cambios
    r = client.get(f'/expenses/{ids[0]}')
    data = r.json()    
    assert r.status_code == 200, r.text    
    assert data['amount'] == 500.0
    assert data['date'] == "2026-04-01"

def test_patch_raise_if_invalid_id(client):
    r = client.patch(f'/expenses/invented_id', json={'amount': 500, 'date_': "2026-04-01"})
    assert r.status_code == 404, r.text
    
def test_patch_returns_expense_with_no_changes_but_updated_at_if_no_changes_included(client):
    ids = seed_expenses(client)
    
    # comprobamos campo antes de cambio
    r = client.get(f'/expenses/{ids[0]}')
    data = r.json()    
    assert r.status_code == 200, r.text    
    assert data['amount'] == 400.0
    assert data['date'] == "2026-02-01"
    
    # pasamos patch
    r = client.patch(f'/expenses/{ids[0]}', json={})
    assert r.status_code == 200, r.text
    data = r.json() 
    assert data['amount'] == 400.0
    assert data['date'] == "2026-02-01"
    assert data['id'] == ids[0]
    assert data['updated_at'] is not None