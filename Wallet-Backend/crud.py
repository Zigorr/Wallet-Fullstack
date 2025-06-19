from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
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
