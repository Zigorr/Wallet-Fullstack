import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Currency(str, enum.Enum):
    USD = "USD"
    EGP = "EGP" 
    GBP = "GBP"
    EUR = "EUR"

class RecurrenceFrequency(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    default_currency = Column(Enum(Currency), nullable=False, default=Currency.USD)
    
    accounts = relationship("Account", back_populates="owner")
    categories = relationship("Category", back_populates="owner")
    transactions = relationship("Transaction", back_populates="owner")
    recurring_transactions = relationship("RecurringTransaction", back_populates="owner")

class AccountType(str, enum.Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    INVESTMENT = "INVESTMENT"
    CASH = "CASH"

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    initial_balance = Column(Float, default=0.0)
    currency = Column(Enum(Currency), nullable=False, default=Currency.USD)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    recurring_transactions = relationship("RecurringTransaction", back_populates="account")

class CategoryType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    recurring_transactions = relationship("RecurringTransaction", back_populates="category")

class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(String)
    currency = Column(Enum(Currency), nullable=False, default=Currency.USD)
    recurring_transaction_id = Column(Integer, ForeignKey("recurring_transactions.id"), nullable=True)
    
    account_id = Column(Integer, ForeignKey("accounts.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True) # Nullable for transfers
    owner_id = Column(Integer, ForeignKey("users.id"))

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    owner = relationship("User", back_populates="transactions")
    recurring_transaction = relationship("RecurringTransaction", back_populates="generated_transactions")

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # User-friendly name for the recurring transaction
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(String)
    currency = Column(Enum(Currency), nullable=False, default=Currency.USD)
    frequency = Column(Enum(RecurrenceFrequency), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)  # Nullable for indefinite recurrence
    next_due_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    account_id = Column(Integer, ForeignKey("accounts.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Nullable for transfers
    owner_id = Column(Integer, ForeignKey("users.id"))

    account = relationship("Account", back_populates="recurring_transactions")
    category = relationship("Category", back_populates="recurring_transactions")
    owner = relationship("User", back_populates="recurring_transactions")
    generated_transactions = relationship("Transaction", back_populates="recurring_transaction")
