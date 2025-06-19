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
