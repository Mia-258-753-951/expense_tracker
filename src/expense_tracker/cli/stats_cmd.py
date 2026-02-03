import calendar
from datetime import date

import typer

from expense_tracker.services.filters import StatsBy, StatsFilter
from expense_tracker.services.stats_service import ExpenseStats

app = typer.Typer()
stat_serv: ExpenseStats | None = None


def init(service: ExpenseStats) -> None:
    global stat_serv
    stat_serv = service


def parse_month(value: str) -> date:
    # value "YYYY-MM"
    try:
        y, m = value.split("-")
        return date(int(y), int(m), 1)
    except Exception as e:
        raise typer.BadParameter("Month must be YYYY-MM") from e


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)  # "YYYY-MM-DD"
    except ValueError as e:
        raise typer.BadParameter("Date must be YYYY-MM-DD") from e


@app.command()
def month_stats(month: str = typer.Option(..., "--month")):
    assert stat_serv is not None

    start_date = parse_month(month)
    # calendar.monthrange devuelve una tupla: (día_semana_inicio, numero_de_dias)
    # El índice [1] nos da exactamente cuántos días tiene ese mes y año
    last_day = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date.replace(day=last_day)

    filter_ = StatsFilter(
        start_date=start_date,
        end_date=end_date,
    )

    stats = stat_serv.month_stats(month_year=filter_)
    label_w = 22
    col_w = 8
    # pasamos los top cat y wal a str para no presentar listas al usuario
    assert stats.top_categories is not None and stats.top_wallets is not None
    top_cas_str = ",".join(stats.top_categories)
    top_wals_str = ",".join(stats.top_wallets)
    header = f"{start_date.year}-{start_date.month} stats:"
    typer.echo(header)
    typer.echo("-" * len(header))
    typer.echo(f"- {'Total amount spent:':<{label_w}} {stats.total_amount * 100:>{col_w}.2f} €")
    typer.echo(f"- {'Number of payments:':<{label_w}} {stats.count:>{col_w}}")
    typer.echo(f"- {'Top 3 categories:':<{label_w}} {top_cas_str}")
    typer.echo(f"- {'top 3 wallets:':<{label_w}} {top_wals_str}")


@app.command()
def stats_range(
    start_date: str = typer.Option(..., "--from", "-f"),
    end_date: str = typer.Option(..., "--to", "-t"),
    by: StatsBy = typer.Option(None, "--by", "-b"),
):
    assert stat_serv is not None
    if not start_date or not end_date:
        raise ValueError("Required a date range.")

    start_date_ = parse_date(start_date)
    end_date_ = parse_date(end_date)

    if by is None:
        stat = stat_serv.summary_range(start_date_, end_date_)
        label_w = 20
        col_w = 8
        header = f"{'Range:':<{label_w}} {start_date} -> {end_date}"
        typer.echo(header)
        typer.echo("-" * len(header))
        typer.echo(f"{'Total:':<{label_w}} {stat.total_amount:>{col_w}.2f} €")
        typer.echo(f"{'Number of expenses:':<{label_w}} {stat.count:>{col_w}}")
        typer.echo(f"{'Expense average:':<{label_w}} {stat.average:>{col_w}} €")

    elif by == StatsBy.CATEGORY:
        stat = stat_serv.by_category(start_date_, end_date_)
        label_w = 35
        col_w = 12
        header = f"{'CATEGORY':<{label_w}}{'TOTAL(€)':>{col_w}}{'%':>{col_w}}{'COUNT':>{col_w}}"
        typer.echo(header)
        typer.echo("-" * len(header))
        for k in stat:
            typer.echo(
                f"{k.key:<{label_w}}"
                f"{k.total * 100:>{col_w}.2f} "
                f"{k.percent:>{col_w}.2f}%"
                f"{k.count:>{col_w}}"
            )

    elif by == StatsBy.WALLET:
        stat = stat_serv.by_wallet(start_date_, end_date_)
        label_w = 35
        col_w = 12
        header = f"{'WALLET':<{label_w}}{'TOTAL(€)':>{col_w}}{'%':>{col_w}}{'COUNT':>{col_w}}"
        typer.echo(header)
        typer.echo("-" * len(header))
        for k in stat:
            typer.echo(
                f"{k.key:<{label_w}}"
                f"{k.total * 100:>{col_w}.2f} "
                f"{k.percent:>{col_w}.2f}%"
                f"{k.count:>{col_w}}"
            )

    elif by == StatsBy.DAY:
        stat = stat_serv.by_day(start_date_, end_date_)
        label_w = 15
        col_w = 12
        header = f"{'DATE':<{label_w}}{'TOTAL':>{col_w}}{'COUNT':>{col_w}}"
        typer.echo(header)
        typer.echo("-" * len(header))
        for k in stat:
            typer.echo(f"{k.key:<{label_w}}{k.total * 100:>{col_w}}{k.count:>{col_w}}")


@app.command()
def stats_budget(
    month: str = typer.Option("--month", "-m"),
    limit: float = typer.Option(..., "--limit", "-l"),
    warn_at: int = typer.Option(75, "--warn-at"),
):
    assert stat_serv is not None
    y, m = month.split("-")

    stat = stat_serv.budget_month(year=y, month=m, limit=limit, warn_at=warn_at)

    col_w = 12
    typer.echo(f"Month: {f'{stat.year}-{stat.month}':>{col_w}}")
    typer.echo(f"Budget: {stat.limit:>{col_w}} €")
    typer.echo(f"Spent: {stat.spent:.2f:>{col_w}} €")
    typer.echo(f"Remaining: {stat.remaining:.2f:>{col_w}} €")
    typer.echo(f"Used: {stat.used:>{col_w}}%")
    typer.echo(f"Status: {stat.status:>{col_w}}")
