from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import schemas, crud, models
from ..database import get_db
from ..utils import get_current_active_user

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new transaction for the current user.
    """
    if transaction.category not in current_user.categories:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this category")

    return crud.create_user_transaction(db=db, transaction=transaction, user_id=current_user.id)

@router.post("/transfers", status_code=status.HTTP_201_CREATED)
def create_transfer(
    transfer: schemas.TransactionTransferCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new transfer between two of the current user's accounts.
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

    return crud.create_user_transfer(db=db, transfer=transfer, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Transaction])
def read_user_transactions(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve transactions for the current user.
    """
    return crud.get_user_transactions(db=db, user_id=current_user.id, skip=skip, limit=limit) 