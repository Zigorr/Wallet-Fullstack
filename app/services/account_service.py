from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import json
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.core.cache import cache_manager, cached
from fastapi import HTTPException, status

class AccountService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @cached(expire=300, key_prefix="user_accounts")
    async def get_user_accounts(self, user_id: str) -> List[AccountResponse]:
        """Get all accounts for a user with caching"""
        result = await self.db.execute(
            select(Account)
            .options(selectinload(Account.transactions))  # Eager load if needed
            .where(Account.user_id == user_id, Account.is_active == True)
            .order_by(Account.created_at.desc())
        )
        accounts = result.scalars().all()
        return [AccountResponse.from_orm(account) for account in accounts]

    async def get_user_account_ids(self, user_id: str) -> List[str]:
        """Get user's account IDs with caching for quick access"""
        cache_key = f"user_account_ids:{user_id}"
        cached_ids = await cache_manager.get(cache_key)
        
        if cached_ids:
            try:
                return json.loads(cached_ids)
            except json.JSONDecodeError:
                pass
        
        # Query database
        result = await self.db.execute(
            select(Account.id).where(
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        account_ids = [row[0] for row in result.fetchall()]
        
        # Cache for 5 minutes
        await cache_manager.set(cache_key, json.dumps(account_ids), expire=300)
        
        return account_ids

    async def get_account_by_id(self, account_id: str, user_id: str) -> AccountResponse:
        """Get account by ID with user validation"""
        result = await self.db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return AccountResponse.from_orm(account)

    async def create_account(self, account_data: AccountCreate, user_id: str) -> AccountResponse:
        """Create a new account and invalidate cache"""
        # Check if account name already exists for user
        existing_result = await self.db.execute(
            select(Account.id).where(
                Account.user_id == user_id,
                Account.name == account_data.name,
                Account.is_active == True
            )
        )
        
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account with this name already exists"
            )
        
        # Create account
        account = Account(
            user_id=user_id,
            name=account_data.name,
            account_type=account_data.account_type,
            balance=account_data.balance,
            currency=account_data.currency,
            bank_name=account_data.bank_name,
            color=account_data.color,
            icon=account_data.icon,
            is_active=True
        )
        
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        
        # Invalidate user's account cache
        await self._invalidate_user_account_cache(user_id)
        
        return AccountResponse.from_orm(account)

    async def update_account(self, account_id: str, account_data: AccountUpdate, user_id: str) -> AccountResponse:
        """Update an account and invalidate cache"""
        # Get account with user validation
        result = await self.db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Check name uniqueness if name is being updated
        if account_data.name and account_data.name != account.name:
            existing_result = await self.db.execute(
                select(Account.id).where(
                    Account.user_id == user_id,
                    Account.name == account_data.name,
                    Account.is_active == True,
                    Account.id != account_id
                )
            )
            
            if existing_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account with this name already exists"
                )
        
        # Update fields
        update_data = account_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        
        await self.db.commit()
        await self.db.refresh(account)
        
        # Invalidate user's account cache
        await self._invalidate_user_account_cache(user_id)
        
        return AccountResponse.from_orm(account)

    async def delete_account(self, account_id: str, user_id: str) -> dict:
        """Soft delete an account and invalidate cache"""
        # Get account with user validation
        result = await self.db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Soft delete
        account.is_active = False
        await self.db.commit()
        
        # Invalidate user's account cache
        await self._invalidate_user_account_cache(user_id)
        
        return {"message": "Account deleted successfully"}

    async def get_account_statistics(self, user_id: str) -> dict:
        """Get account statistics with caching"""
        cache_key = f"user_account_stats:{user_id}"
        cached_stats = await cache_manager.get(cache_key)
        
        if cached_stats:
            try:
                return json.loads(cached_stats)
            except json.JSONDecodeError:
                pass
        
        # Query database for statistics
        result = await self.db.execute(
            select(
                func.count(Account.id).label('total_accounts'),
                func.sum(func.case([(Account.balance > 0, Account.balance)], else_=0)).label('total_assets'),
                func.sum(func.case([(Account.balance < 0, -Account.balance)], else_=0)).label('total_liabilities'),
                func.sum(Account.balance).label('net_worth')
            )
            .where(Account.user_id == user_id, Account.is_active == True)
        )
        
        row = result.first()
        stats = {
            "total_accounts": int(row.total_accounts or 0),
            "total_assets": float(row.total_assets or 0),
            "total_liabilities": float(row.total_liabilities or 0),
            "net_worth": float(row.net_worth or 0)
        }
        
        # Cache for 2 minutes (accounts don't change as frequently)
        await cache_manager.set(cache_key, json.dumps(stats), expire=120)
        
        return stats

    async def _invalidate_user_account_cache(self, user_id: str):
        """Invalidate all account-related cache for a user"""
        cache_keys = [
            f"user_accounts:{user_id}",
            f"user_account_ids:{user_id}",
            f"user_account_stats:{user_id}"
        ]
        
        for key in cache_keys:
            await cache_manager.delete(key) 