from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from datetime import datetime
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.category import Category
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse, TransactionWithDetails
from fastapi import HTTPException, status

class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_account_ids(self, user_id: str) -> List[str]:
        """Get user's account IDs with caching potential"""
        result = await self.db.execute(
            select(Account.id).where(
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        return [row[0] for row in result.fetchall()]

    async def get_user_transactions(self, user_id: str, limit: int = 100, offset: int = 0) -> List[TransactionResponse]:
        """Get transactions with pagination and optimized queries"""
        account_ids = await self.get_user_account_ids(user_id)
        
        if not account_ids:
            return []
        
        # Optimized query with eager loading
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))  # Eager load category
            .where(Transaction.account_id.in_(account_ids))
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
            .offset(offset)
        )
        transactions = result.scalars().all()
        return [TransactionResponse.from_orm(transaction) for transaction in transactions]

    async def get_user_transactions_with_details(self, user_id: str, limit: int = 100, offset: int = 0) -> List[TransactionWithDetails]:
        """Get transactions with account and category details using joins"""
        account_ids = await self.get_user_account_ids(user_id)
        
        if not account_ids:
            return []
        
        # Single optimized query with joins
        result = await self.db.execute(
            select(
                Transaction,
                Account.name.label('account_name'),
                Category.name.label('category_name')
            )
            .join(Account, Transaction.account_id == Account.id)
            .outerjoin(Category, Transaction.category_id == Category.id)
            .where(Transaction.account_id.in_(account_ids))
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
            .offset(offset)
        )
        
        transactions_with_details = []
        for row in result:
            transaction = row.Transaction
            transaction_dict = TransactionWithDetails.from_orm(transaction).dict()
            transaction_dict['account_name'] = row.account_name
            transaction_dict['category_name'] = row.category_name
            transactions_with_details.append(TransactionWithDetails(**transaction_dict))
        
        return transactions_with_details

    async def get_transaction_by_id(self, transaction_id: str, user_id: str) -> TransactionResponse:
        """Get transaction with optimized user validation"""
        # Single query with join to validate ownership
        result = await self.db.execute(
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Transaction.id == transaction_id,
                Account.user_id == user_id
            )
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return TransactionResponse.from_orm(transaction)

    async def create_transaction(self, transaction_data: TransactionCreate, user_id: str) -> TransactionResponse:
        """Create transaction with validation optimization"""
        # Single query to validate account ownership
        account_result = await self.db.execute(
            select(Account).where(
                Account.id == transaction_data.account_id,
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        account = account_result.scalar_one_or_none()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or inactive"
            )
        
        # Validate category if provided (with optimized query)
        if transaction_data.category_id:
            category_result = await self.db.execute(
                select(Category.id).where(
                    Category.id == transaction_data.category_id,
                    Category.is_active == True
                )
            )
            if not category_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found or inactive"
                )
        
        # Create transaction
        transaction = Transaction(
            account_id=transaction_data.account_id,
            amount=transaction_data.amount,
            description=transaction_data.description,
            notes=transaction_data.notes,
            transaction_date=transaction_data.transaction_date or datetime.utcnow(),
            merchant_name=transaction_data.merchant_name,
            category_id=transaction_data.category_id
        )
        
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return TransactionResponse.from_orm(transaction)

    async def bulk_create_transactions(self, transactions_data: List[TransactionCreate], user_id: str) -> List[TransactionResponse]:
        """Bulk create transactions for better performance"""
        # Validate all accounts belong to user
        account_ids = list(set(tx.account_id for tx in transactions_data))
        valid_accounts = await self.db.execute(
            select(Account.id).where(
                Account.id.in_(account_ids),
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        valid_account_ids = {row[0] for row in valid_accounts.fetchall()}
        
        # Validate all categories exist
        category_ids = list(set(tx.category_id for tx in transactions_data if tx.category_id))
        if category_ids:
            valid_categories = await self.db.execute(
                select(Category.id).where(
                    Category.id.in_(category_ids),
                    Category.is_active == True
                )
            )
            valid_category_ids = {row[0] for row in valid_categories.fetchall()}
        else:
            valid_category_ids = set()
        
        # Create transactions
        transactions = []
        for tx_data in transactions_data:
            if tx_data.account_id not in valid_account_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid account ID: {tx_data.account_id}"
                )
            
            if tx_data.category_id and tx_data.category_id not in valid_category_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category ID: {tx_data.category_id}"
                )
            
            transaction = Transaction(
                account_id=tx_data.account_id,
                amount=tx_data.amount,
                description=tx_data.description,
                notes=tx_data.notes,
                transaction_date=tx_data.transaction_date or datetime.utcnow(),
                merchant_name=tx_data.merchant_name,
                category_id=tx_data.category_id
            )
            transactions.append(transaction)
        
        # Bulk insert
        self.db.add_all(transactions)
        await self.db.commit()
        
        # Refresh all transactions
        for transaction in transactions:
            await self.db.refresh(transaction)
        
        return [TransactionResponse.from_orm(transaction) for transaction in transactions]

    async def update_transaction(self, transaction_id: str, transaction_data: TransactionUpdate, user_id: str) -> TransactionResponse:
        """Update transaction with optimized validation"""
        # Get transaction with account validation in single query
        result = await self.db.execute(
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Transaction.id == transaction_id,
                Account.user_id == user_id
            )
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Validate category if being updated
        if transaction_data.category_id:
            category_result = await self.db.execute(
                select(Category.id).where(
                    Category.id == transaction_data.category_id,
                    Category.is_active == True
                )
            )
            if not category_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found or inactive"
                )
        
        # Update fields
        update_data = transaction_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return TransactionResponse.from_orm(transaction)

    async def delete_transaction(self, transaction_id: str, user_id: str) -> dict:
        """Delete transaction with optimized validation"""
        result = await self.db.execute(
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Transaction.id == transaction_id,
                Account.user_id == user_id
            )
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        await self.db.delete(transaction)
        await self.db.commit()
        
        return {"message": "Transaction deleted successfully"}

    async def get_transaction_statistics(self, user_id: str, start_date: datetime, end_date: datetime) -> dict:
        """Get aggregated transaction statistics with optimized queries"""
        account_ids = await self.get_user_account_ids(user_id)
        
        if not account_ids:
            return {"total_income": 0, "total_expenses": 0, "transaction_count": 0}
        
        # Single query for all statistics
        result = await self.db.execute(
            select(
                func.sum(func.case([(Transaction.amount > 0, Transaction.amount)], else_=0)).label('total_income'),
                func.sum(func.case([(Transaction.amount < 0, -Transaction.amount)], else_=0)).label('total_expenses'),
                func.count(Transaction.id).label('transaction_count')
            )
            .where(
                Transaction.account_id.in_(account_ids),
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        )
        
        row = result.first()
        return {
            "total_income": float(row.total_income or 0),
            "total_expenses": float(row.total_expenses or 0),
            "transaction_count": int(row.transaction_count or 0)
        } 