from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
import models
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction_for_user(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new transaction for the current authenticated user.
    """
    # Basic validation to ensure the user owns the account being used
    account = crud.get_account(db, account_id=transaction.account_id)
    if not account or account.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this account")
    
    # Optional validation for category
    if transaction.category_id:
        category = crud.get_category(db, category_id=transaction.category_id)
        if not category or category.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this category")

    return crud.create_user_transaction(db=db, transaction=transaction, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Transaction])
def read_user_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve all transactions for the current authenticated user.
    """
    transactions = crud.get_transactions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return transactions

@router.get("/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve a specific transaction by its ID.
    """
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_transaction.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this transaction")
    return db_transaction

@router.put("/{transaction_id}", response_model=schemas.Transaction)
def update_user_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a transaction for the current authenticated user.
    """
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_transaction.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this transaction")
    return crud.update_transaction(db=db, transaction_id=transaction_id, transaction_update=transaction_update)

@router.delete("/{transaction_id}", response_model=schemas.Transaction)
def delete_user_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a transaction for the current authenticated user.
    """
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_transaction.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this transaction")
    return crud.delete_transaction(db=db, transaction_id=transaction_id)
