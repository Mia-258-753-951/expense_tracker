from pydantic import BaseModel
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException

from expense_tracker.domain.models import Expense
from expense_tracker.domain.errors import ExpenseNotFound
from expense_tracker.services.filters import ExpenseFilter, ExpenseUpdate
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
    
class ExpenseUpdated(BaseModel):
    id: str
    date: date
    amount: float
    category: str
    wallet: str
    note: str | None
    currency: str
    updated_at: datetime
    
class ExpenseListFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    category_: str | None = None
    wallet_: str | None = None
    limit_: int | None = None  # nº máximo de registros a mostrar
    sort_: str | None = None
    
class ExpensePatch(BaseModel):
    date_: date | None = None
    amount: float | None = None
    category: str | None = None
    wallet: str | None = None
    note: str | None = None
    currency: str | None = None

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
    
@router.post('', response_model=ExpenseId, status_code=201)
def create_expense(
    payload: ExpenseIn,
    service: ExpenseService=Depends(get_expense_service),
):
    expense_data = payload.model_dump()
    expense_data['amount'] = int(round(expense_data['amount'] * 100))
    expense = Expense(**expense_data)    
    
    new_id = service.add_expense(expense)
    
    return ExpenseId(id=new_id)

@router.get('/{expense_id}', response_model=ExpenseOut)
def get_expense_by_id(
    expense_id: str,
    service: ExpenseService=Depends(get_expense_service)
    ):
    expense = service.get_expense(expense_id)
    
    if expense is None:
        raise HTTPException(status_code=404, detail='Expense not found.')
    
    return ExpenseOut(
        id=expense.id,
        date=expense.date,
        amount=expense.amount / 100,
        category=expense.category,
        wallet=expense.wallet,
        note=expense.note,
        currency=expense.currency
    )
    
@router.delete('/{expense_id}', status_code=204)
def delete_expense(
    expense_id: str,
    service: ExpenseService=Depends(get_expense_service)
):
    try:
        service.delete_expense(expense_id)
    except ExpenseNotFound:
        raise HTTPException(status_code=404, detail='Expense not found.')
    
@router.patch('/{expense_id}', response_model=ExpenseUpdated)
def update_expense(
    expense_id: str,
    payload: ExpensePatch,
    service: ExpenseService=Depends(get_expense_service)
):
    changes = payload.model_dump(exclude_unset=True)
    if 'amount' in changes:
        changes['amount'] = int(round(changes['amount'] * 100))    
    to_update= ExpenseUpdate(id=expense_id, **changes)
    
    try:
        updated = service.update_expense(to_update)
        assert updated.updated_at is not None
        
    except ExpenseNotFound:
        raise HTTPException(status_code=404, detail='Expense not found.')
    
    return ExpenseUpdated(
        id=updated.id,
        date=updated.date,
        amount=updated.amount / 100,
        category=updated.category,
        wallet=updated.wallet,
        note=updated.note,
        currency=updated.currency,
        updated_at=updated.updated_at,
    )
    
    