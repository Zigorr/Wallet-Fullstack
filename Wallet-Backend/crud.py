from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple currency conversion rates (in a real app, you'd fetch these from an API)
CURRENCY_RATES = {
    models.Currency.USD: 1.0,  # Base currency
    models.Currency.EUR: 0.85,
    models.Currency.GBP: 0.73,
    models.Currency.EGP: 30.9,
}

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        username=user.username,
        default_currency=user.default_currency
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def get_accounts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Account).filter(models.Account.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_account(db: Session, account: schemas.AccountCreate, user_id: int):
    db_account = models.Account(**account.dict(), owner_id=user_id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def update_account(db: Session, account_id: int, account_update: schemas.AccountUpdate):
    db_account = get_account(db, account_id)
    if db_account:
        update_data = account_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_account, key, value)
        db.commit()
        db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int):
    db_account = get_account(db, account_id)
    if db_account:
        db.delete(db_account)
        db.commit()
    return db_account

# Category CRUD functions
def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_categories_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Category).filter(models.Category.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(**category.dict(), owner_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate):
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

# Transaction CRUD functions
def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.dict(), owner_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction_update: schemas.TransactionUpdate):
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        update_data = transaction_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction

def convert_currency(amount: float, from_currency: models.Currency, to_currency: models.Currency) -> float:
    """Convert amount from one currency to another using exchange rates"""
    if from_currency == to_currency:
        return amount
    
    # Convert to USD first, then to target currency
    usd_amount = amount / CURRENCY_RATES[from_currency]
    converted_amount = usd_amount * CURRENCY_RATES[to_currency]
    
    return round(converted_amount, 2)

def create_user_transfer(db: Session, transfer: schemas.TransactionTransferCreate, user_id: int):
    # Get the source and destination accounts to check their currencies
    from_account = get_account(db, transfer.from_account_id)
    to_account = get_account(db, transfer.to_account_id)
    
    if not from_account or not to_account:
        raise ValueError("Invalid account IDs")
    
    # Use user-specified converted amount or calculate automatically
    if transfer.converted_amount is not None:
        converted_amount = transfer.converted_amount
    else:
        # Calculate the converted amount using default rates
        converted_amount = convert_currency(
            transfer.amount, 
            from_account.currency, 
            to_account.currency
        )
    
    # Create the expense transaction (money leaving source account)
    expense_transaction = models.Transaction(
        amount=transfer.amount,
        type=models.TransactionType.TRANSFER,
        description=transfer.description or f"Transfer to {to_account.name}",
        currency=from_account.currency,  # Use source account currency
        account_id=transfer.from_account_id,
        category_id=None,
        owner_id=user_id
    )
    
    # Create the income transaction (money entering destination account)
    income_transaction = models.Transaction(
        amount=converted_amount,
        type=models.TransactionType.TRANSFER,
        description=transfer.description or f"Transfer from {from_account.name}",
        currency=to_account.currency,  # Use destination account currency
        account_id=transfer.to_account_id,
        category_id=None,
        owner_id=user_id
    )
    
    db.add(expense_transaction)
    db.add(income_transaction)
    db.commit()
    db.refresh(expense_transaction)
    db.refresh(income_transaction)
    
    return {
        "expense": expense_transaction, 
        "income": income_transaction,
        "exchange_rate": converted_amount / transfer.amount if transfer.amount > 0 else 1.0,
        "converted_amount": converted_amount
    }

# Recurring Transaction CRUD functions
def get_recurring_transaction(db: Session, recurring_transaction_id: int):
    return db.query(models.RecurringTransaction).filter(models.RecurringTransaction.id == recurring_transaction_id).first()

def get_recurring_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.RecurringTransaction).filter(models.RecurringTransaction.owner_id == user_id).offset(skip).limit(limit).all()

def get_active_recurring_transactions_by_user(db: Session, user_id: int):
    return db.query(models.RecurringTransaction).filter(
        models.RecurringTransaction.owner_id == user_id,
        models.RecurringTransaction.is_active == True
    ).all()

def calculate_next_due_date(start_date: datetime, frequency: models.RecurrenceFrequency) -> datetime:
    """Calculate the next due date based on frequency"""
    if frequency == models.RecurrenceFrequency.DAILY:
        return start_date + timedelta(days=1)
    elif frequency == models.RecurrenceFrequency.WEEKLY:
        return start_date + timedelta(weeks=1)
    elif frequency == models.RecurrenceFrequency.MONTHLY:
        return start_date + relativedelta(months=1)
    elif frequency == models.RecurrenceFrequency.QUARTERLY:
        return start_date + relativedelta(months=3)
    elif frequency == models.RecurrenceFrequency.YEARLY:
        return start_date + relativedelta(years=1)
    else:
        return start_date + timedelta(days=1)  # Default to daily

def create_user_recurring_transaction(db: Session, recurring_transaction: schemas.RecurringTransactionCreate, user_id: int):
    # Calculate the next due date
    next_due_date = calculate_next_due_date(recurring_transaction.start_date, recurring_transaction.frequency)
    
    db_recurring_transaction = models.RecurringTransaction(
        **recurring_transaction.dict(),
        owner_id=user_id,
        next_due_date=next_due_date
    )
    db.add(db_recurring_transaction)
    db.commit()
    db.refresh(db_recurring_transaction)
    return db_recurring_transaction

def update_recurring_transaction(db: Session, recurring_transaction_id: int, recurring_transaction_update: schemas.RecurringTransactionUpdate):
    db_recurring_transaction = get_recurring_transaction(db, recurring_transaction_id)
    if db_recurring_transaction:
        update_data = recurring_transaction_update.dict(exclude_unset=True)
        
        # If start_date or frequency is updated, recalculate next_due_date
        if 'start_date' in update_data or 'frequency' in update_data:
            start_date = update_data.get('start_date', db_recurring_transaction.start_date)
            frequency = update_data.get('frequency', db_recurring_transaction.frequency)
            update_data['next_due_date'] = calculate_next_due_date(start_date, frequency)
        
        for key, value in update_data.items():
            setattr(db_recurring_transaction, key, value)
        db.commit()
        db.refresh(db_recurring_transaction)
    return db_recurring_transaction

def delete_recurring_transaction(db: Session, recurring_transaction_id: int):
    db_recurring_transaction = get_recurring_transaction(db, recurring_transaction_id)
    if db_recurring_transaction:
        db.delete(db_recurring_transaction)
        db.commit()
    return db_recurring_transaction

def get_due_recurring_transactions(db: Session, current_date: datetime = None):
    """Get all recurring transactions that are due for processing"""
    if current_date is None:
        current_date = datetime.now()
    
    return db.query(models.RecurringTransaction).filter(
        models.RecurringTransaction.is_active == True,
        models.RecurringTransaction.next_due_date <= current_date
    ).all()

def process_recurring_transaction(db: Session, recurring_transaction: models.RecurringTransaction):
    """Process a single recurring transaction by creating a new transaction and updating the next due date"""
    # Create the actual transaction
    new_transaction = models.Transaction(
        amount=recurring_transaction.amount,
        type=recurring_transaction.type,
        description=recurring_transaction.description,
        currency=recurring_transaction.currency,
        account_id=recurring_transaction.account_id,
        category_id=recurring_transaction.category_id,
        owner_id=recurring_transaction.owner_id,
        recurring_transaction_id=recurring_transaction.id
    )
    
    db.add(new_transaction)
    
    # Update the next due date
    next_due_date = calculate_next_due_date(recurring_transaction.next_due_date, recurring_transaction.frequency)
    
    # Check if we need to deactivate (if end_date is set and we've passed it)
    if recurring_transaction.end_date and next_due_date > recurring_transaction.end_date:
        recurring_transaction.is_active = False
    else:
        recurring_transaction.next_due_date = next_due_date
    
    db.commit()
    db.refresh(new_transaction)
    db.refresh(recurring_transaction)
    
    return new_transaction
