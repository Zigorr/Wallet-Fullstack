from sqlalchemy import Column, String, Boolean, DateTime, func, ForeignKey, Enum, Numeric, Text
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class AccountType(str, enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    LOAN = "loan"
    CASH = "cash"
    OTHER = "other"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False, default=AccountType.CHECKING)
    balance = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default="USD")
    bank_name = Column(String(100))
    account_number = Column(String(50))
    routing_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    color = Column(String(7), default="#3B82F6")  # Hex color
    icon = Column(String(50), default="credit-card")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan") 