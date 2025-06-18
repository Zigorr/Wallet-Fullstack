from sqlalchemy import Column, String, Boolean, DateTime, func, Enum, Text
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False)
    category_type = Column(Enum(CategoryType), nullable=False, default=CategoryType.EXPENSE)
    color = Column(String(7), default="#6B7280")  # Hex color
    icon = Column(String(50), default="folder")
    is_system = Column(Boolean, default=False)  # System-defined categories
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category") 