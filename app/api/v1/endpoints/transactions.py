from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, date
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.transaction import (
    TransactionCreate, 
    TransactionUpdate, 
    TransactionResponse, 
    TransactionWithDetails
)
from app.services.transaction_service import TransactionService

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    include_details: bool = Query(False, description="Include account and category names"),
    limit: int = Query(100, ge=1, le=1000, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all transactions for the current user with pagination"""
    transaction_service = TransactionService(db)
    
    if include_details:
        transactions = await transaction_service.get_user_transactions_with_details(
            current_user.id, limit=limit, offset=offset
        )
        return transactions
    else:
        return await transaction_service.get_user_transactions(
            current_user.id, limit=limit, offset=offset
        )

@router.get("/statistics")
async def get_transaction_statistics(
    start_date: date = Query(..., description="Start date for statistics"),
    end_date: date = Query(..., description="End date for statistics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transaction statistics for a date range"""
    transaction_service = TransactionService(db)
    
    # Convert dates to datetime for database query
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    return await transaction_service.get_transaction_statistics(
        current_user.id, start_datetime, end_datetime
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transaction"""
    transaction_service = TransactionService(db)
    return await transaction_service.get_transaction_by_id(transaction_id, current_user.id)

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction"""
    transaction_service = TransactionService(db)
    return await transaction_service.create_transaction(transaction, current_user.id)

@router.post("/bulk", response_model=List[TransactionResponse])
async def create_transactions_bulk(
    transactions: List[TransactionCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple transactions in a single request for better performance"""
    if len(transactions) > 100:
        raise HTTPException(
            status_code=400,
            detail="Cannot create more than 100 transactions at once"
        )
    
    transaction_service = TransactionService(db)
    return await transaction_service.bulk_create_transactions(transactions, current_user.id)

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a transaction"""
    transaction_service = TransactionService(db)
    return await transaction_service.update_transaction(transaction_id, transaction, current_user.id)

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a transaction"""
    transaction_service = TransactionService(db)
    return await transaction_service.delete_transaction(transaction_id, current_user.id) 