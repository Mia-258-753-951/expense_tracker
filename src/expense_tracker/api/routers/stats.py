
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import date
import calendar
from typing import Annotated

from expense_tracker.api.deps import get_stats_service
from expense_tracker.services.stats_service import ExpenseStats

router = APIRouter(prefix='/stats', tags=['stats'])

class StatsInRange(BaseModel):
    total: float
    count: int
    average: float
    
class MonthStats(BaseModel):
    total: float
    count: int
    average: float
    top_categories: list[str]
    top_wallets: list[str]


@router.get('/health')
def stats_hello():
    return {'status': 'Ok'}

@router.get('/range', response_model=StatsInRange)
def stats_in_range(
    start_date: date,
    end_date: date,
    service: ExpenseStats=Depends(get_stats_service)
):
    
    stats = service.summary_range(start_date, end_date)
    
    return StatsInRange(
        total=stats.total_amount,
        count=stats.count,
        average=stats.average,
    )

Year = Annotated[int, Field(ge=2000, le=2100, description='YYYY')]
Month = Annotated[int, Field(ge=1, le=12)]

@router.get('/month', response_model= MonthStats)
def month_stats(
    year: Year,
    month: Month,
    service: ExpenseStats=Depends(get_stats_service)
):
    start_date = date(year, month, 1)   
    last_day = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date.replace(day=last_day)
        
    stats = service.month_stats(start_date, end_date)    
        
    return MonthStats(
        total=stats.total_amount,
        count=stats.count,
        average=stats.average,
        top_categories=stats.top_categories,
        top_wallets=stats.top_wallets
    )
        
    