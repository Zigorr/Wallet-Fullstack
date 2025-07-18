from typing import List, Dict
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
@router.post("", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)  # Handle without trailing slash
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

@router.post("/transfers", status_code=status.HTTP_201_CREATED, response_model=schemas.TransactionTransferResponse)
def create_transfer(
    transfer: schemas.TransactionTransferCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new transfer between two of the current user's accounts.
    Supports automatic currency conversion if accounts use different currencies.
    """
    if transfer.from_account_id == transfer.to_account_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source and destination accounts cannot be the same.")

    # Verify user owns both accounts
    from_account = crud.get_account(db, account_id=transfer.from_account_id)
    to_account = crud.get_account(db, account_id=transfer.to_account_id)

    if not from_account or from_account.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use the source account.")
    
    if not to_account or to_account.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use the destination account.")

    try:
        result = crud.create_user_transfer(db=db, transfer=transfer, user_id=current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/exchange-rates", response_model=Dict[str, float])
def get_exchange_rates(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get current exchange rates for currency conversion.
    """
    return {currency.value: rate for currency, rate in crud.CURRENCY_RATES.items()}

@router.get("/", response_model=List[schemas.Transaction])
@router.get("", response_model=List[schemas.Transaction])  # Handle without trailing slash
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
