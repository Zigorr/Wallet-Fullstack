from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from models import AccountType, CategoryType, TransactionType

# --- Base Schemas ---

class UserBase(BaseModel):
    email: EmailStr
    username: str

class AccountBase(BaseModel):
    name: str
    type: AccountType
    initial_balance: float = 0.0

class CategoryBase(BaseModel):
    name: str
    type: CategoryType

class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    description: Optional[str] = None
    account_id: int
    category_id: Optional[int] = None

# --- Schemas for Creating new objects (what the API receives) ---

class UserCreate(UserBase):
    password: str

class AccountCreate(AccountBase):
    pass

class CategoryCreate(CategoryBase):
    pass

class TransactionCreate(TransactionBase):
    pass

class TransactionTransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = None

# --- Schemas for Updating objects ---

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AccountType] = None
    initial_balance: Optional[float] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[CategoryType] = None

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None

# --- Schemas for Reading objects (what the API sends back) ---

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Account(AccountBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Category(CategoryBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Transaction(TransactionBase):
    id: int
    date: datetime
    owner_id: int

    class Config:
        from_attributes = True

# --- Schemas for Authentication & Config ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

class ValidationConfig(BaseModel):
    password_regex: str
    password_message: str
