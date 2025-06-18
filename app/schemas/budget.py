from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.budget import BudgetPeriod

class BudgetBase(BaseModel):
    amount: float = Field(..., gt=0, description="Budget amount (must be positive)")
    period: BudgetPeriod = Field(..., description="Budget period (weekly, monthly, yearly)")
    start_date: datetime = Field(..., description="Budget start date")
    end_date: datetime = Field(..., description="Budget end date")
    description: Optional[str] = Field(None, max_length=500, description="Budget description")

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class BudgetCreate(BudgetBase):
    category_id: str = Field(..., description="Category ID for this budget")

class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[BudgetPeriod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class BudgetResponse(BudgetBase):
    id: str
    user_id: str
    category_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Extended response with related data
class BudgetWithDetails(BudgetResponse):
    category_name: Optional[str] = None
    spent_amount: Optional[float] = None  # Amount spent in this budget period
    remaining_amount: Optional[float] = None  # Amount remaining 