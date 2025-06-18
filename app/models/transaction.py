from sqlalchemy import Column, String, DateTime, func, ForeignKey, Numeric, Text, Date, Float, Index
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    notes = Column(Text)
    transaction_date = Column(Date, nullable=False)
    
    # Optional fields for bank sync
    external_id = Column(String(100))  # Bank transaction ID
    merchant_name = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    
    # Database indexes for performance optimization
    __table_args__ = (
        # Index for getting user's transactions (via account_id) ordered by date
        Index('idx_account_date', 'account_id', 'transaction_date'),
        # Index for filtering by date range
        Index('idx_transaction_date', 'transaction_date'),
        # Index for filtering by category
        Index('idx_category_date', 'category_id', 'transaction_date'),
        # Composite index for common queries
        Index('idx_account_category_date', 'account_id', 'category_id', 'transaction_date'),
        # Index for amount-based queries (statistics)
        Index('idx_account_amount_date', 'account_id', 'amount', 'transaction_date'),
    ) 