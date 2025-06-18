from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from fastapi import HTTPException, status

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Default system categories
    DEFAULT_CATEGORIES = [
        # Income categories
        {"name": "Salary", "category_type": CategoryType.INCOME, "color": "#10b981", "icon": "dollar-sign"},
        {"name": "Freelance", "category_type": CategoryType.INCOME, "color": "#10b981", "icon": "briefcase"},
        {"name": "Investment", "category_type": CategoryType.INCOME, "color": "#10b981", "icon": "trending-up"},
        {"name": "Other Income", "category_type": CategoryType.INCOME, "color": "#10b981", "icon": "plus"},
        
        # Expense categories
        {"name": "Food & Dining", "category_type": CategoryType.EXPENSE, "color": "#ef4444", "icon": "utensils"},
        {"name": "Groceries", "category_type": CategoryType.EXPENSE, "color": "#ef4444", "icon": "shopping-cart"},
        {"name": "Transportation", "category_type": CategoryType.EXPENSE, "color": "#f59e0b", "icon": "car"},
        {"name": "Shopping", "category_type": CategoryType.EXPENSE, "color": "#8b5cf6", "icon": "shopping-bag"},
        {"name": "Entertainment", "category_type": CategoryType.EXPENSE, "color": "#06b6d4", "icon": "film"},
        {"name": "Bills & Utilities", "category_type": CategoryType.EXPENSE, "color": "#dc2626", "icon": "file-text"},
        {"name": "Healthcare", "category_type": CategoryType.EXPENSE, "color": "#059669", "icon": "heart"},
        {"name": "Education", "category_type": CategoryType.EXPENSE, "color": "#7c3aed", "icon": "book"},
        {"name": "Travel", "category_type": CategoryType.EXPENSE, "color": "#0891b2", "icon": "plane"},
        {"name": "Home & Garden", "category_type": CategoryType.EXPENSE, "color": "#65a30d", "icon": "home"},
        {"name": "Personal Care", "category_type": CategoryType.EXPENSE, "color": "#db2777", "icon": "user"},
        {"name": "Other Expenses", "category_type": CategoryType.EXPENSE, "color": "#6b7280", "icon": "more-horizontal"},
        
        # Transfer categories
        {"name": "Account Transfer", "category_type": CategoryType.TRANSFER, "color": "#3b82f6", "icon": "arrow-right"},
        {"name": "Savings", "category_type": CategoryType.TRANSFER, "color": "#3b82f6", "icon": "piggy-bank"},
    ]

    async def ensure_default_categories(self):
        """Create default system categories if they don't exist"""
        for cat_data in self.DEFAULT_CATEGORIES:
            # Check if category already exists
            result = await self.db.execute(
                select(Category).where(
                    Category.name == cat_data["name"],
                    Category.is_system == True
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                category = Category(
                    name=cat_data["name"],
                    category_type=cat_data["category_type"],
                    color=cat_data["color"],
                    icon=cat_data["icon"],
                    is_system=True,
                    is_active=True
                )
                self.db.add(category)
        
        await self.db.commit()

    async def get_all_categories(self, user_id: str) -> List[CategoryResponse]:
        """Get all categories (system + user categories)"""
        # Ensure default categories exist
        await self.ensure_default_categories()
        
        # Get all system categories and user's custom categories
        result = await self.db.execute(
            select(Category).where(
                or_(
                    Category.is_system == True,
                    Category.user_id == user_id
                )
            ).where(Category.is_active == True)
            .order_by(Category.category_type, Category.name)
        )
        categories = result.scalars().all()
        return [CategoryResponse.from_orm(category) for category in categories]

    async def get_category_by_id(self, category_id: str, user_id: str) -> CategoryResponse:
        """Get a specific category"""
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                or_(
                    Category.is_system == True,
                    Category.user_id == user_id
                )
            )
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return CategoryResponse.from_orm(category)

    async def create_category(self, category_data: CategoryCreate, user_id: str) -> CategoryResponse:
        """Create a new custom category"""
        # Check if user already has a category with this name
        result = await self.db.execute(
            select(Category).where(
                Category.name == category_data.name,
                Category.user_id == user_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        category = Category(
            name=category_data.name,
            category_type=category_data.category_type,
            color=category_data.color,
            icon=category_data.icon,
            description=category_data.description,
            user_id=user_id,
            is_system=False,
            is_active=True
        )
        
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        return CategoryResponse.from_orm(category)

    async def update_category(self, category_id: str, category_data: CategoryUpdate, user_id: str) -> CategoryResponse:
        """Update a category (only custom categories can be updated)"""
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.is_system == False
            )
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or cannot be updated"
            )
        
        # Check name uniqueness if name is being updated
        if category_data.name and category_data.name != category.name:
            name_check = await self.db.execute(
                select(Category).where(
                    Category.name == category_data.name,
                    Category.user_id == user_id,
                    Category.id != category_id
                )
            )
            if name_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists"
                )
        
        # Update fields
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await self.db.commit()
        await self.db.refresh(category)
        
        return CategoryResponse.from_orm(category)

    async def delete_category(self, category_id: str, user_id: str) -> dict:
        """Delete a category (only custom categories can be deleted)"""
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.is_system == False
            )
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or cannot be deleted"
            )
        
        # Soft delete by setting is_active to False
        category.is_active = False
        await self.db.commit()
        
        return {"message": "Category deleted successfully"} 