
from helpers import seed_expenses

def test_stats_health(client):
    r = client.get('/stats/health')
    
    assert r.status_code == 200
    
def test_get_stats_in_range_returns_summary(client):
    seed_expenses(client)    
    r = client.get('/stats/range', params={'start_date': '2026-02-01', 'end_date': '2026-02-28'})
    
    data = r.json()
    assert r.status_code == 200, r.text
    assert data['total'] == 1100.0
    assert data['count'] == 2
    assert data['average'] == 550.0
    
def test_get_month_stats_returns_month_stats_details(client):
    seed_expenses(client)    
    r = client.get('/stats/month', params={'year': '2026', 'month': 2})
    
    data = r.json()
    assert r.status_code == 200, r.text    
    assert data['total'] == 1100.0
    assert data['count'] == 2
    assert data['average'] == 550.0
    assert set(data["top_categories"]) == {"food", "pet"}  # evitamos el orden por si empate

def test_stats_range_empty_returns_zeroes(client):
    
    r = client.get('/stats/range', params={'start_date': '2026-02-02', 'end_date': '2026-02-07'})
    data = r.json()
    assert r.status_code == 200, r.text

    assert data['total'] == 0
    assert data['count'] == 0
    assert data['average'] == 0
    
def test_month_empty_returns_zeroes(client):
    
    r = client.get('/stats/month', params={'year': '2026', 'month': 1})
    data = r.json()
    assert r.status_code == 200, r.text

    assert data['total'] == 0
    assert data['count'] == 0
    assert data['average'] == 0
    assert data["top_categories"] == []
    assert data["top_wallets"] == []

def test_start_date_empty_get_422_response_status(client):
    r = client.get('/stats/range', params={'end_date': '2026-02-01'})
    assert r.status_code == 422, r.text
    
def test_end_date_empty_get_422_response_status(client):
    r = client.get('/stats/range', params={'end_date': '2026-02-01'})
    assert r.status_code == 422, r.text



def test_invalid_month_get_422_response_status(client):
        
    r = client.get('/stats/month', params={'year': '2026', 'month': 0})
    assert r.status_code == 422, r.text
    
def test_invalid_range_get_422_response_status(client):
    seed_expenses(client)
    
    r = client.get('/stats/range', params={'start_date': '2026-02-02', 'end_date': '2026-02-01'})
    
    assert r.status_code == 422, r.text

