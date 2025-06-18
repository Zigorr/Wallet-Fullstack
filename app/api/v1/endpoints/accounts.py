from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.services.account_service import AccountService

router = APIRouter()

def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService(db)

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get all accounts for the current user"""
    return await account_service.get_user_accounts(current_user.id)

@router.post("/", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Create a new account"""
    return await account_service.create_account(account_data, current_user.id)

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get a specific account"""
    return await account_service.get_account_by_id(account_id, current_user.id)

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Update an account"""
    return await account_service.update_account(account_id, account_data, current_user.id)

@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Delete an account (soft delete)"""
    return await account_service.delete_account(account_id, current_user.id) 