
import typer
from datetime import date
from typing import Any


from expense_tracker.infrastructure.memory_repo import InMemoryExpenseRepository
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.domain.models import Expense
from expense_tracker.services.filters import ExpenseFilter, SortMethods, UNSET, ExpenseUpdate
app = typer.Typer(name='Expense Tracker')

exp_repo = InMemoryExpenseRepository()
exp_serv = ExpenseService(exp_repo)

@app.command()
def add(
    amount: float, 
    date_: date | None = typer.Option(None, '--date', '-d', formats=['%Y-%m-%d']), 
    category: str = typer.Option(..., '--category', '-c'), 
    wallet: str = typer.Option('casa', '--wallet', '-w'),
    note: str | None = typer.Option(None, '--note', '-n'),
    currency: str = typer.Option('EUR', '--currency'),
    ):
    
    if date_ is None:
        date_ = date.today()

    exp = Expense(
        date=date_,
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
    start_date: date|None = typer.Option(None, '--from-date', formats=['%Y-%m-%d']), 
    end_date: date|None = typer.Option(None, '--to-date', formats=['%Y-%m-%d']), 
    category: str|None = typer.Option(None, '--category', '-c'), 
    wallet: str|None = typer.Option(None, '--wallet', '-w'),
    num_reg: int|None = typer.Option(None, '--limit'),
    sort_method: SortMethods|None = typer.Option(None, '--sort', '-s'),
    ):

    filters = ExpenseFilter(
        from_date_=start_date,
        to_date_=end_date,
        category_=category,
        wallet_=wallet,
        limit_=num_reg,
        sort_=sort_method.value if sort_method is not None else None,
    )
    
    exps = exp_serv.list_expenses(filters)
    
    typer.echo(f'List of Expenses:\n')
    for e in exps:
        typer.echo(f'- {e}')

@app.command()        
def update(
    id: str,
    amount: float | None = typer.Option(None), 
    date_: date | None = typer.Option(None, '--date', '-d', formats=['%Y-%m-%d']), 
    category: str | None = typer.Option(None, '--category', '-c'), 
    wallet: str | None = typer.Option(None, '--wallet', '-w'),
    note: str | None | Any = typer.Option(UNSET, '--note', '-n'),
    currency: str | None = typer.Option(None, '--currency'),
    ):
        try:
            
            amount = int(round(amount*100)) if amount is not None else None
            patch = ExpenseUpdate(
                id=id,
                amount=amount,
                date_=date_,
                category=category,
                wallet=wallet,
                note=note,
                currency=currency,                
            )
            
            updated = exp_serv.update_expense(patch=patch)            
            
        except:
            typer.echo(f"Expense not found with id {id}")
            raise typer.Exit(code=1)

        typer.echo(f"Updated expense:\n{updated}")
        
@app.command()
def delete(id: str):
    exp = exp_serv.delete_expense(exp_id=id)
    
    if exp is None:
        typer.echo(f'Expense not found with id {id}')
        raise typer.Exit(code=1)
    typer.echo('Deleted expense with id {id}.')
    
