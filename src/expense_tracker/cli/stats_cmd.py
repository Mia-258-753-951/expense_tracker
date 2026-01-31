
import typer
from datetime import date
import calendar
import enum

from expense_tracker.infrastructure.memory_repo import InMemoryExpenseRepository
from expense_tracker.services.stats_service import ExpenseStats
from expense_tracker.services.filters import ExpenseFilter, StatsBy, StatsFilter

app = typer.Typer()

exp_repo = InMemoryExpenseRepository()
stat_serv = ExpenseStats(exp_repo)

@app.command()
def moth_stats(month: date = typer.Option(..., '--moth', formats=['%Y-%m'])):
    start_date= month    
    # calendar.monthrange devuelve una tupla: (día_semana_inicio, numero_de_dias)
    # El índice [1] nos da exactamente cuántos días tiene ese mes y año
    last_day = calendar.monthrange(month.year, month.month)[1]
    end_date = month.replace(day=last_day)
    
    filter_ = StatsFilter(
        start_date=start_date,
        end_date=end_date,
    )
    
    stats = stat_serv.month_stats(month_year=filter_)
    label_w = 22
    col_w = 8
    # pasamos los top cat y wal a str para no presentar listas al usuario
    top_cas_str = ','.join(stats['top_cat'])
    top_wals_str = ','.join(stats['top_wal'])
    header = (f'{month.year}-{month.month} stats:')
    typer.echo(header)
    typer.echo('-' * len(header))    
    typer.echo(f'- {"Total amount spent:":<{label_w}} {stats["total_amount"]:>{col_w}.2f} €')
    typer.echo(f'- {"Number of payments:":<{label_w}} {stats["num_exps"]:>{col_w}}')
    typer.echo(f'- {"Top 3 categories:":<{label_w}} {top_cas_str}')
    typer.echo(f'- {"top 3 wallets:":<{label_w}} {top_wals_str}')

@app.command()
def stats_range(
    start_date: date = typer.Option(..., '--from', '-f', formats=['%Y-%m-%d']),
    end_date: date = typer.Option(..., '--to', '-t', formats=['%Y-%m-%d']),
    by: StatsBy | None = typer.Option(None, '--by', '-b'),
    ):
    if not start_date or not end_date:
        raise ValueError('Required a date range.')
    filter_ = StatsFilter(
        start_date=start_date,
        end_date=end_date, 
        by=by,
    )
    
    app_filter, stats = stat_serv.stats_by(filter_=filter_)
    
    if app_filter is None:
        label_w = 20
        col_w = 8
        header = (f'{"Range:":<{label_w}} {start_date} -> {end_date}')
        typer.echo(header)
        typer.echo('-' * len(header))
        typer.echo(f'{"Total:":<{label_w}} {stats["total_amount"]:>{col_w}.2f} €')
        typer.echo(f'{"Number of expenses:":<{label_w}} {stats["num_exps"]:>{col_w}}')
        typer.echo(f'{"Expense average:":<{label_w}} {stats["average_exp"]:>{col_w}} €')
    
    if app_filter != 'day':
        total_amount = sum(k['total'] for k in stats) * 100
        label_w = 35
        col_w = 12
        header = (f'{app_filter.upper():<{label_w}}{"TOTAL(€)":>{col_w}}{"%":>{col_w}}{"COUNT":>{col_w}}')        
        typer.echo(header)
        typer.echo('-' * len(header))
        for k in stats:
            if not isinstance(k, date):
                typer.echo(
                    f'{k:<{label_w}}'
                    f'{stats[k]["total"]*100:>{col_w}.2f} '
                    f'{stats[k]["total"]*100/total_amount:>{col_w}.2f}%'
                    f'{stats[k]["num"]:>{col_w}}'
                )
    
    if app_filter == 'day':
        label_w = 15
        col_w = 12
        header = (f'{"DATE":<{label_w}}{"TOTAL":>{col_w}}{"COUNT":>{col_w}}')
        typer.echo(header)
        typer.echo('-' * len(header))
        for k in stats:
            typer.echo(
                f'{stats[k]:<{label_w}}'
                f'{stats["total"]*100:>{col_w}}'
                f'{stats["num"]:>{col_w}}'
            )

@app.command()    
def stats_budget(
    month: date = typer.Option('--month', '-m', formats=['%Y-%m']),
    limit: float = typer.Option(..., '--limit', '-l'),
    warn_at: int = typer.Option(75, '--warn-at')
):
    start_date = month
    last_day = calendar.monthrange(month.year, month.month)[1]
    end_date = month.replace(day=last_day)
    
    filter_ = StatsFilter(
        start_date=start_date,
        end_date=end_date,
    )
    
    total_spent = stat_serv.stats_budget(month_year=filter_, limit=limit)
    remain = limit - total_spent
    if  total_spent < warn_at/100 * limit:
        status = 'OK'
    if total_spent < limit:
        status = 'WARNING'
    else:
        status = 'EXCEEDED'
        
    col_w = 12
    typer.echo(f'Month: {month.isoformat():>{col_w}}')
    typer.echo(f'Budget: {limit:>{col_w}} €')
    typer.echo(f'Spent: {total_spent:.2f:>{col_w}} €')
    typer.echo(f'Remaining: {remain:.2f:>{col_w}} €')
    typer.echo(f'Used: {int(round(total_spent/limit)):>{col_w}}%')
    typer.echo(f'Status: {status:>{col_w}}')
