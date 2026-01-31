from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any


class SortMethods(str, Enum):
    AMOUNT = 'amount'
    DATE = 'date'

@dataclass
class ExpenseFilter:
    """
    Define los filtros posibles para el listado de Expenses.
    sort_ para definir tipo de ordenación: 'amount' | 'date'.
    """
    from_date_: date | None = None
    to_date_: date | None = None
    category_: str | None = None
    wallet_: str | None = None
    limit_: int | None = None  # nº máximo de registros a mostrar
    sort_: str | None = None
    
                    
UNSET = object()   # sentinel para patch

@dataclass
class ExpenseUpdate:
    """
    Patch para definir campos que se actualizarán. 
    UNSET define campos Opcinales que no se han incluido en el
    update por parte del usuario, obligando a deefinir None
    expresamente.
    """
    id: str
    amount: int | None = None 
    date_: date | None = None
    category: str | None = None
    wallet: str | None = None
    note: str | None | Any = UNSET
    currency: str | None = None
    
class StatsBy(str, Enum):
    CATEGORY = 'category'
    WALLET = 'wallet'
    DAY = 'day'
    
@dataclass
class StatsFilter:
    start_date: date
    end_date: date
    by: StatsBy | None = None
    

    