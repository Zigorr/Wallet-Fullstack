from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float = Field(..., description="Transaction amount (positive for income, negative for expense)")
    description: str = Field(..., min_length=1, max_length=200, description="Transaction description")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    merchant_name: Optional[str] = Field(None, max_length=100, description="Merchant name")
    transaction_date: Optional[datetime] = Field(None, description="Transaction date (defaults to now)")

class TransactionCreate(TransactionBase):
    account_id: str = Field(..., description="Account ID for this transaction")
    category_id: Optional[str] = Field(None, description="Category ID for this transaction")

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    merchant_name: Optional[str] = Field(None, max_length=100)
    transaction_date: Optional[datetime] = None
    category_id: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    account_id: str
    category_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Extended response with related data
class TransactionWithDetails(TransactionResponse):
    account_name: Optional[str] = None
    category_name: Optional[str] = None 