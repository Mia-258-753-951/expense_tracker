
from fastapi import FastAPI

from expense_tracker.api.routers import expenses
from expense_tracker.api.routers import stats



app = FastAPI(title='Expense Tracker API')

# conectamos los routers
app.include_router(expenses.router)
app.include_router(stats.router)

@app.get('/health')
def hello():
    return {'status': 'OK'}

