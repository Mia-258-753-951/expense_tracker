
import typer

import expense_tracker.cli.expense_cmd as exps
from expense_tracker.cli import stats_cmd as stats
from expense_tracker.infrastructure.memory_repo import InMemoryExpenseRepository
from expense_tracker.services.stats_service import ExpenseStats
from expense_tracker.services.expense_service import ExpenseService


app = typer.Typer()

repo = InMemoryExpenseRepository()
stat_serv = ExpenseStats(repo)
exp_serv = ExpenseService(repo)

exps.init(exp_serv)
stats.init(stat_serv)

app.add_typer(exps.app, name='expenses')
app.add_typer(stats.app, name='stats')



if __name__ == '__main__':
    app()
