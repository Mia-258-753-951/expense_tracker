from pydantic import BaseModel
from datetime import date
from fastapi import APIRouter, Depends

from expense_tracker.domain.models import Expense
from expense_tracker.services.filters import ExpenseFilter
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.api.deps import get_expense_service

router = APIRouter(prefix='/expenses', tags=['expenses'])

class ExpenseIn(BaseModel):
    amount: float
    date: date
    category: str
    wallet: str
    note: str | None = None
    currency: str = 'EUR'
    
class ExpenseId(BaseModel):
    id: str

class ExpenseOut(BaseModel):
    id: str
    date: date
    amount: float
    category: str
    wallet: str
    note: str | None
    currency: str
    
class ExpenseListFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    category_: str | None = None
    wallet_: str | None = None
    limit_: int | None = None  # nº máximo de registros a mostrar
    sort_: str | None = None

@router.get('/health')
def expenses_hello():
    return {'status': 'Ok'}
    
@router.get('', response_model=list[ExpenseOut])
def list_expenses(
    from_: date | None=None,
    to: date | None=None,
    category: str | None=None,
    wallet: str | None = None,
    limit: int | None = None,
    sort: str | None = None,
    service: ExpenseService=Depends(get_expense_service),
):
    filter_ = ExpenseFilter(
                            start_date=from_,
                            end_date=to,
                            category_=category,
                            wallet_=wallet,
                            limit_=limit,
                            sort_=sort,
                            )
    
    items = service.list_expenses(filter_)
    
    return [
        ExpenseOut(
            id=e.id,
            date=e.date,
            amount=e.amount/100,
            category=e.category,
            wallet=e.wallet,
            note=e.note,
            currency=e.currency
        )
            for e in items
        
    ]
    
@router.post('', response_model=ExpenseId)
def create_expense(
    payload: ExpenseIn,
    service: ExpenseService=Depends(get_expense_service),
):
    expense_data = payload.model_dump()
    expense_data['amount'] = int(round(expense_data['amount'] * 100))
    expense = Expense(**expense_data)    
    
    new_id = service.add_expense(expense)
    
    return ExpenseId(id=new_id)
    