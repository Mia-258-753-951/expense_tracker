
from pathlib import Path
import json
from json import JSONDecodeError
from typing import Any
from datetime import date, datetime

from expense_tracker.ports.expense_repo import ExpenseRepository
from expense_tracker.domain.models import Expense

JSON_PATH = Path(__file__).resolve().parents[2] / 'data/expenses.json'

SUPPORTED_SCHEMA_V = 1

class JsonExpenseRepository(ExpenseRepository):
    
    def __init__(self, path: Path = JSON_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        try:
            with self.path.open('r', encoding='utf-8') as f:
                data_=json.load(f)
                if data_['schema_version'] != SUPPORTED_SCHEMA_V:
                    raise ValueError(
                        f"schema_version '{data_['schema_version']}' not supported. Supported version: '{SUPPORTED_SCHEMA_V}'."
                        )
                self.data = self._json_to_data(data_)
        except (FileNotFoundError, JSONDecodeError):
            self.data = {}
    
    def _json_to_data(self, j: dict[str, Any]) -> dict[str, Expense]:
        model = {}
        for e in j['expenses']:
            e['date'] = date.fromisoformat(e['date'])
            e['created_at'] = datetime.fromisoformat(e['created_at'])
            e['updated_at'] = datetime.fromisoformat(e['updated_at']) if e['updated_at'] is not None else None
            model[e['id']] = Expense(**e)
        return model
    
    def _save_json(self, data: dict[str, Expense]) -> None:
        j = {'schema_version': SUPPORTED_SCHEMA_V, 'expenses': []}
        for v in data.values():
            e = {
                'id': v.id,
                'date': v.date.isoformat(),
                'amount': v.amount,
                'category': v.category,
                'wallet': v.wallet,
                'note': v.note,
                'currency': v.currency,
                'created_at': v.created_at.isoformat(),
                'updated_at': v.updated_at.isoformat() if v.updated_at is not None else None,
            }
            j['expenses'].append(e)
        # guardado atómico
        tmp_path = self.path.with_suffix(self.path.suffix + '.tmp')
        with tmp_path.open('w', encoding='utf-8') as f:
            json.dump(j, f, ensure_ascii=False, indent=2)
        tmp_path.replace(self.path)

    def add(self, exp: Expense) -> str:
        self.data[exp.id] = exp
        self._save_json(self.data)
        return exp.id

    def get(self, exp_id: str) -> Expense | None:
        return self.data.get(exp_id)

    def list_all(self) -> list[Expense]:
        return [e for e in self.data.values()]

    def update(self, modified_exp: Expense) -> Expense:
        modified_exp.updated_at = datetime.now()
        self.data[modified_exp.id] = modified_exp
        self._save_json(self.data)
        return modified_exp

    def delete(self, exp_id: str) -> None:
        del self.data[exp_id]
        self._save_json(self.data)
        return None
