from sqlalchemy import Column, String, DateTime, func, ForeignKey, Numeric, Enum, Date, Boolean
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class BudgetPeriod(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    period = Column(Enum(BudgetPeriod), nullable=False, default=BudgetPeriod.MONTHLY)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # Optional for recurring budgets
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets") 