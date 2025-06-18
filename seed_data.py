import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db, engine
from app.models.user import User
from app.models.account import Account, AccountType
from app.models.transaction import Transaction
from app.models.category import Category, CategoryType
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random

async def seed_database():
    """Seed the database with sample data"""
    print("🌱 Starting database seeding...")
    
    async with AsyncSession(engine) as db:
        # Check if demo user already exists
        result = await db.execute(select(User).where(User.email == "demo@wallet.com"))
        demo_user = result.scalar_one_or_none()
        
        if demo_user:
            print("✅ Demo user already exists")
        else:
            # Create demo user
            demo_user = User(
                email="demo@wallet.com",
                hashed_password=get_password_hash("demo123"),
                first_name="Demo",
                last_name="User",
                currency="USD"
            )
            db.add(demo_user)
            await db.commit()
            await db.refresh(demo_user)
            print("✅ Created demo user: demo@wallet.com / demo123")
        
        # Check if accounts already exist
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == demo_user.id)
        )
        existing_accounts = accounts_result.scalars().all()
        
        if existing_accounts:
            print("✅ Demo accounts already exist")
            accounts = existing_accounts
        else:
            # Create sample accounts
            accounts = [
                Account(
                    name="Main Checking",
                    account_type=AccountType.CHECKING,
                    balance=5420.50,
                    currency="USD",
                    bank_name="Chase Bank",
                    color="#3b82f6",
                    icon="checking",
                    user_id=demo_user.id,
                    is_active=True
                ),
                Account(
                    name="Savings Account",
                    account_type=AccountType.SAVINGS,
                    balance=12840.75,
                    currency="USD",
                    bank_name="Wells Fargo",
                    color="#10b981",
                    icon="savings",
                    user_id=demo_user.id,
                    is_active=True
                ),
                Account(
                    name="Credit Card",
                    account_type=AccountType.CREDIT_CARD,
                    balance=2340.20,
                    currency="USD",
                    bank_name="American Express",
                    color="#ef4444",
                    icon="credit",
                    user_id=demo_user.id,
                    is_active=True
                )
            ]
            
            for account in accounts:
                db.add(account)
            
            await db.commit()
            for account in accounts:
                await db.refresh(account)
            print("✅ Created demo accounts")
        
        # Check if categories exist (they should be created automatically)
        categories_result = await db.execute(
            select(Category).where(Category.is_system == True)
        )
        categories = categories_result.scalars().all()
        
        if not categories:
            print("ℹ️  No categories found - they will be created when first accessed")
        else:
            print(f"✅ Found {len(categories)} system categories")
        
        # Check if transactions already exist
        transactions_result = await db.execute(
            select(Transaction).where(Transaction.account_id.in_([acc.id for acc in accounts]))
        )
        existing_transactions = transactions_result.scalars().all()
        
        if existing_transactions:
            print("✅ Demo transactions already exist")
        else:
            # Create sample transactions
            sample_transactions = [
                # Recent transactions
                {
                    "account_id": accounts[0].id,  # Checking
                    "amount": -45.50,
                    "description": "Grocery Store - Weekly Shopping",
                    "transaction_date": datetime.now() - timedelta(days=1),
                },
                {
                    "account_id": accounts[0].id,  # Checking
                    "amount": 2500.00,
                    "description": "Salary Deposit",
                    "transaction_date": datetime.now() - timedelta(days=2),
                },
                {
                    "account_id": accounts[0].id,  # Checking
                    "amount": -120.00,
                    "description": "Gas Station",
                    "transaction_date": datetime.now() - timedelta(days=3),
                },
                {
                    "account_id": accounts[1].id,  # Savings
                    "amount": 500.00,
                    "description": "Monthly Savings Transfer",
                    "transaction_date": datetime.now() - timedelta(days=5),
                },
                {
                    "account_id": accounts[2].id,  # Credit Card
                    "amount": -89.99,
                    "description": "Online Shopping - Amazon",
                    "transaction_date": datetime.now() - timedelta(days=7),
                },
                # Older transactions for history
                {
                    "account_id": accounts[0].id,
                    "amount": -850.00,
                    "description": "Rent Payment",
                    "transaction_date": datetime.now() - timedelta(days=10),
                },
                {
                    "account_id": accounts[0].id,
                    "amount": -25.99,
                    "description": "Netflix Subscription",
                    "transaction_date": datetime.now() - timedelta(days=15),
                },
                {
                    "account_id": accounts[1].id,
                    "amount": 50.00,
                    "description": "Interest Payment",
                    "transaction_date": datetime.now() - timedelta(days=20),
                },
            ]
            
            transactions = []
            for tx_data in sample_transactions:
                transaction = Transaction(
                    account_id=tx_data["account_id"],
                    amount=tx_data["amount"],
                    description=tx_data["description"],
                    transaction_date=tx_data["transaction_date"],
                )
                db.add(transaction)
                transactions.append(transaction)
            
            await db.commit()
            print(f"✅ Created {len(transactions)} demo transactions")
        
        print("🎉 Database seeding completed!")
        print(f"🔑 Demo login: demo@wallet.com / demo123")
        print(f"📊 Accounts: {len(accounts)}")
        print(f"💳 Transactions: {len(existing_transactions) if existing_transactions else len(sample_transactions)}")

if __name__ == "__main__":
    asyncio.run(seed_database()) 