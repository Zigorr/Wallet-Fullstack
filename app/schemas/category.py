from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.category import CategoryType

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    category_type: CategoryType = Field(..., description="Type of category (income, expense, transfer)")
    color: str = Field(default="#6B7280", regex="^#[0-9A-Fa-f]{6}$", description="Hex color code")
    icon: str = Field(default="folder", max_length=50, description="Icon identifier")
    description: Optional[str] = Field(None, max_length=500, description="Category description")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: str
    is_system: bool
    is_active: bool
    user_id: Optional[str]  # NULL for system categories
    created_at: datetime
    
    class Config:
        from_attributes = True 