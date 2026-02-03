
from datetime import date
from typing import Any

import typer

from expense_tracker.domain.models import Expense
from expense_tracker.services.filters import UNSET, ExpenseFilter, ExpenseUpdate, SortMethods
from expense_tracker.services.expense_service import ExpenseService

app = typer.Typer()
exp_serv: ExpenseService | None = None

def init(service: ExpenseService) -> None:
    global exp_serv
    exp_serv = service


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)  # "YYYY-MM-DD"
    except ValueError as e:
        raise typer.BadParameter("Date must be YYYY-MM-DD") from e


@app.command()
def add(
    amount: float, 
    date_: str  = typer.Option(None, '--date', '-d'), 
    category: str = typer.Option(..., '--category', '-c'), 
    wallet: str = typer.Option('casa', '--wallet', '-w'),
    note: str = typer.Option(None, '--note', '-n'),
    currency: str = typer.Option('EUR', '--currency'),
    ):
    assert exp_serv is not None
    
    d: date | None = None if date_ is None else parse_date(date_)
    
    if d is None:
        d = date.today()

    exp = Expense(
        date=d,
        amount=int(round(amount*100)),
        category=category,
        wallet=wallet,
        note=note,
        currency=currency,
    )
    new_id = exp_serv.add_expense(exp=exp)
    
    typer.echo(f'New Expense added with id {new_id}')

@app.command()
def list(
    start_date: str = typer.Option(None, '--from-date'), 
    end_date: str = typer.Option(None, '--to-date'), 
    category: str = typer.Option(None, '--category', '-c'), 
    wallet: str = typer.Option(None, '--wallet', '-w'),
    num_reg: int = typer.Option(None, '--limit'),
    sort_method: SortMethods = typer.Option(None, '--sort', '-s'),
    ):
    assert exp_serv is not None
    
    filters = ExpenseFilter(
        from_date_=parse_date(start_date) if start_date is not None else None,
        to_date_=parse_date(end_date) if end_date is not None else None,
        category_=category,
        wallet_=wallet,
        limit_=num_reg,
        sort_=sort_method.value if sort_method is not None else None,
    )
    
    exps = exp_serv.list_expenses(filters)
    
    typer.echo('List of Expenses:\n')
    for e in exps:
        typer.echo(f'- {e}')
        
@app.command()
def get(id: str):
    assert exp_serv is not None
    
    exp = exp_serv.get_expense(exp_id=id)
    if exp is None:
        typer.echo(f'Expense not found with id {id}')
        raise typer.Exit(code=1)
    typer.echo(f'- Expense {id}:\n{exp}')

@app.command()        
def update(
    id: str,
    amount: float = typer.Option(None), 
    date_: str = typer.Option(None, '--date', '-d'), 
    category: str = typer.Option(None, '--category', '-c'), 
    wallet: str  = typer.Option(None, '--wallet', '-w'),
    note: str = typer.Option('__UNSET__', '--note', '-n'),
    currency: str = typer.Option(None, '--currency'),
    ):
    assert exp_serv is not None
    try:        
        amount_ = int(round(amount*100)) if amount is not None else None
        patch = ExpenseUpdate(
            id=id,
            amount=amount_,
            date_=parse_date(date_) if date_ is not None else None,
            category=category,
            wallet=wallet,
            note=UNSET if note == '__UNSET__' else note,
            currency=currency,                
        )
        
        updated = exp_serv.update_expense(patch=patch)            
        
    except Exception:
        typer.echo(f"Expense not found with id {id}")
        raise typer.Exit(code=1) from None

    typer.echo(f"Updated expense:\n{updated}")
        
@app.command()
def delete(id: str):
    assert exp_serv is not None
    
    exp = exp_serv.get_expense(exp_id=id)    
    if exp is None:
        typer.echo(f'Expense not found with id {id}')
        raise typer.Exit(code=1)
    exp_serv.delete_expense(id)
    typer.echo('Deleted expense with id {id}.')
    
