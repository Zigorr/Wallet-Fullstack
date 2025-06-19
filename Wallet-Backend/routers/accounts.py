from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=schemas.Account)
def create_account(
    account: schemas.AccountCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.create_user_account(db=db, account=account, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Account])
def read_accounts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    accounts = crud.get_accounts(db, user_id=current_user.id, skip=skip, limit=limit)
    return accounts

@router.get("/{account_id}", response_model=schemas.Account)
def read_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if db_account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this account")
    return db_account

@router.put("/{account_id}", response_model=schemas.Account)
def update_account(
    account_id: int, 
    account: schemas.AccountUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if db_account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this account")
    return crud.update_account(db=db, account_id=account_id, account_update=account)

@router.delete("/{account_id}", response_model=schemas.Account)
def delete_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if db_account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this account")
    return crud.delete_account(db=db, account_id=account_id)
