
def seed_expenses(client):
    payloads = [
        {
            "amount": 400,
            "date": "2026-02-01",
            "category": "pet",
            "wallet": "home",
        },
        {
            "amount": 700,
            "date": "2026-02-15",
            "category": "food",
            "wallet": "home",
        },
        {
            "amount": 400,
            "date": "2026-03-01",
            "category": "pet",
            "wallet": "bank",
        },
    ]
    ids = []
    for p in payloads:
        r = client.post("/expenses", json=p)
        assert r.status_code == 201
        ids.append(r.json()['id'])   # hacemos que devuelva los ids para tests que lo necesiten
    return ids
