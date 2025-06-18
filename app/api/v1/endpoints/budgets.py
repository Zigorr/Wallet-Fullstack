from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.budget import Budget, BudgetPeriod
from app.models.category import Category
from app.api.v1.endpoints.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

# Schemas
class BudgetCreate(BaseModel):
    category_id: str
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None

class BudgetUpdate(BaseModel):
    amount: Optional[float] = None
    period: Optional[BudgetPeriod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/")
async def get_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all budgets for the current user"""
    result = await db.execute(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.is_active == True
        ).order_by(Budget.created_at.desc())
    )
    budgets = result.scalars().all()
    return budgets

@router.post("/")
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new budget"""
    # Verify the category exists and belongs to user or is system category
    category_result = await db.execute(
        select(Category).where(
            Category.id == budget_data.category_id,
            (Category.user_id == current_user.id) | (Category.is_system == True)
        )
    )
    category = category_result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    budget = Budget(
        category_id=budget_data.category_id,
        amount=budget_data.amount,
        period=budget_data.period,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        description=budget_data.description,
        user_id=current_user.id,
        is_active=True
    )
    
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    
    return budget

@router.get("/{budget_id}")
async def get_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific budget"""
    result = await db.execute(
        select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == current_user.id
        )
    )
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return budget

@router.put("/{budget_id}")
async def update_budget(
    budget_id: str,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a budget"""
    result = await db.execute(
        select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == current_user.id
        )
    )
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    # Update fields
    update_data = budget_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)
    
    await db.commit()
    await db.refresh(budget)
    
    return budget

@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a budget (soft delete)"""
    result = await db.execute(
        select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == current_user.id
        )
    )
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    # Soft delete by setting is_active to False
    budget.is_active = False
    await db.commit()
    
    return {"message": "Budget deleted successfully"} 