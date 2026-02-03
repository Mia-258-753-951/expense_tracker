from typer.testing import CliRunner

from expense_tracker.cli.main import app

runner = CliRunner()


def test_cli_help_works():
    r = runner.invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "expenses" in r.stdout
    assert "stats" in r.stdout


def test_expenses_list_runs():
    r = runner.invoke(app, ["expenses", "list"])
    assert r.exit_code == 0


def test_stats_month_stats_runs():
    r = runner.invoke(app, ["stats", "month-stats", "--month", "2026-01"])
    assert r.exit_code == 0
