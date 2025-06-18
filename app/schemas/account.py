from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.account import AccountType

class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Account name")
    account_type: AccountType = Field(..., description="Type of account")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Currency code")
    bank_name: Optional[str] = Field(None, max_length=100, description="Bank name")
    color: str = Field(default="#3b82f6", regex="^#[0-9A-Fa-f]{6}$", description="Hex color code")
    icon: str = Field(default="wallet", max_length=50, description="Icon identifier")

class AccountCreate(AccountBase):
    balance: float = Field(default=0.0, description="Initial account balance")

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    balance: Optional[float] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    bank_name: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class AccountResponse(AccountBase):
    id: str
    user_id: str
    balance: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True 