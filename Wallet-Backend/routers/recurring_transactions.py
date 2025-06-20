from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

import crud
import schemas
import models
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/recurring-transactions",
    tags=["recurring-transactions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.RecurringTransaction, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=schemas.RecurringTransaction, status_code=status.HTTP_201_CREATED)  # Handle without trailing slash
def create_recurring_transaction_for_user(
    recurring_transaction: schemas.RecurringTransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new recurring transaction for the current authenticated user.
    """
    # Validate user owns the account
    account = crud.get_account(db, account_id=recurring_transaction.account_id)
    if not account or account.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this account")
    
    # Optional validation for category
    if recurring_transaction.category_id:
        category = crud.get_category(db, category_id=recurring_transaction.category_id)
        if not category or category.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this category")

    return crud.create_user_recurring_transaction(db=db, recurring_transaction=recurring_transaction, user_id=current_user.id)

@router.get("/", response_model=List[schemas.RecurringTransaction])
@router.get("", response_model=List[schemas.RecurringTransaction])  # Handle without trailing slash
def read_user_recurring_transactions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve all recurring transactions for the current authenticated user.
    """
    if active_only:
        recurring_transactions = crud.get_active_recurring_transactions_by_user(db, user_id=current_user.id)
    else:
        recurring_transactions = crud.get_recurring_transactions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return recurring_transactions

@router.get("/{recurring_transaction_id}", response_model=schemas.RecurringTransaction)
def read_recurring_transaction(
    recurring_transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve a specific recurring transaction by its ID.
    """
    db_recurring_transaction = crud.get_recurring_transaction(db, recurring_transaction_id=recurring_transaction_id)
    if db_recurring_transaction is None:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    if db_recurring_transaction.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this recurring transaction")
    return db_recurring_transaction

@router.put("/{recurring_transaction_id}", response_model=schemas.RecurringTransaction)
def update_user_recurring_transaction(
    recurring_transaction_id: int,
    recurring_transaction_update: schemas.RecurringTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a recurring transaction for the current authenticated user.
    """
    db_recurring_transaction = crud.get_recurring_transaction(db, recurring_transaction_id=recurring_transaction_id)
    if db_recurring_transaction is None:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    if db_recurring_transaction.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this recurring transaction")
    
    # Validate account ownership if being updated
    if recurring_transaction_update.account_id:
        account = crud.get_account(db, account_id=recurring_transaction_update.account_id)
        if not account or account.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this account")
    
    # Validate category ownership if being updated
    if recurring_transaction_update.category_id:
        category = crud.get_category(db, category_id=recurring_transaction_update.category_id)
        if not category or category.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this category")
    
    return crud.update_recurring_transaction(db=db, recurring_transaction_id=recurring_transaction_id, recurring_transaction_update=recurring_transaction_update)

@router.delete("/{recurring_transaction_id}", response_model=schemas.RecurringTransaction)
def delete_user_recurring_transaction(
    recurring_transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a recurring transaction for the current authenticated user.
    """
    db_recurring_transaction = crud.get_recurring_transaction(db, recurring_transaction_id=recurring_transaction_id)
    if db_recurring_transaction is None:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    if db_recurring_transaction.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this recurring transaction")
    return crud.delete_recurring_transaction(db=db, recurring_transaction_id=recurring_transaction_id)

@router.post("/process-due", status_code=status.HTTP_200_OK)
def process_due_recurring_transactions(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Process all due recurring transactions for all users.
    This would typically be called by a scheduled job, but can be manually triggered.
    """
    # Get all due recurring transactions (not just for current user - this is an admin-like function)
    due_transactions = crud.get_due_recurring_transactions(db)
    
    processed_count = 0
    for recurring_transaction in due_transactions:
        try:
            crud.process_recurring_transaction(db, recurring_transaction)
            processed_count += 1
        except Exception as e:
            # Log error but continue processing others
            print(f"Error processing recurring transaction {recurring_transaction.id}: {str(e)}")
    
    return {
        "message": f"Processed {processed_count} recurring transactions",
        "processed_count": processed_count,
        "total_due": len(due_transactions)
    }

@router.post("/{recurring_transaction_id}/process", response_model=schemas.Transaction)
def process_single_recurring_transaction(
    recurring_transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Manually process a single recurring transaction (create the actual transaction).
    """
    db_recurring_transaction = crud.get_recurring_transaction(db, recurring_transaction_id=recurring_transaction_id)
    if db_recurring_transaction is None:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    if db_recurring_transaction.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to process this recurring transaction")
    
    if not db_recurring_transaction.is_active:
        raise HTTPException(status_code=400, detail="Cannot process inactive recurring transaction")
    
    new_transaction = crud.process_recurring_transaction(db, db_recurring_transaction)
    return new_transaction 