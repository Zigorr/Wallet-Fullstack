#!/usr/bin/env python3
"""
Migration script to help move data from local PostgreSQL to Supabase.
This script helps export your current data and provides instructions for Supabase setup.
"""

import os
import sys
from sqlalchemy import create_engine, text
import json
from datetime import datetime
from config import settings

def export_data_to_json():
    """Export current database data to JSON files for backup/migration."""
    try:
        # Connect to current database
        engine = create_engine(settings.DATABASE_URL)
        
        # Create exports directory
        export_dir = "data_export"
        os.makedirs(export_dir, exist_ok=True)
        
        # List of tables to export
        tables = [
            "users",
            "accounts", 
            "categories",
            "transactions",
            "recurring_transactions"
        ]
        
        exported_data = {}
        
        with engine.connect() as conn:
            for table in tables:
                try:
                    # Check if table exists
                    result = conn.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"))
                    table_exists = result.scalar()
                    
                    if table_exists:
                        # Export table data
                        result = conn.execute(text(f"SELECT * FROM {table}"))
                        rows = result.fetchall()
                        columns = result.keys()
                        
                        # Convert to list of dictionaries
                        table_data = []
                        for row in rows:
                            row_dict = {}
                            for i, col in enumerate(columns):
                                value = row[i]
                                # Handle datetime objects
                                if isinstance(value, datetime):
                                    value = value.isoformat()
                                row_dict[col] = value
                            table_data.append(row_dict)
                        
                        exported_data[table] = table_data
                        print(f"✓ Exported {len(table_data)} records from {table}")
                    else:
                        print(f"⚠ Table {table} does not exist, skipping...")
                        
                except Exception as e:
                    print(f"✗ Error exporting {table}: {e}")
        
        # Save to JSON file
        export_file = os.path.join(export_dir, f"wallet_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(export_file, 'w') as f:
            json.dump(exported_data, f, indent=2, default=str)
        
        print(f"\n✓ Data exported to: {export_file}")
        return export_file
        
    except Exception as e:
        print(f"✗ Export failed: {e}")
        return None

def print_supabase_setup_instructions():
    """Print step-by-step Supabase setup instructions."""
    print("\n" + "="*60)
    print("SUPABASE SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. Create Supabase Account:")
    print("   - Go to https://supabase.com")
    print("   - Sign up for a free account")
    
    print("\n2. Create New Project:")
    print("   - Click 'New Project'")
    print("   - Choose your organization")
    print("   - Enter project name (e.g., 'wallet-app')")
    print("   - Enter a strong database password")
    print("   - Select a region close to you")
    print("   - Click 'Create new project'")
    
    print("\n3. Get Connection Details:")
    print("   - Go to Settings > Database")
    print("   - Copy the 'Connection string' (URI format)")
    print("   - Go to Settings > API")
    print("   - Copy the 'Project URL' and 'anon public' key")
    
    print("\n4. Update Environment Variables:")
    print("   Create a .env file in Wallet-Backend/ with:")
    print("   ```")
    print("   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres")
    print("   SUPABASE_URL=https://[PROJECT-REF].supabase.co")
    print("   SUPABASE_KEY=[YOUR-ANON-KEY]")
    print("   SECRET_KEY=your-secret-key-here-make-it-long-and-random")
    print("   ALGORITHM=HS256")
    print("   ACCESS_TOKEN_EXPIRE_MINUTES=30")
    print("   LOG_LEVEL=INFO")
    print("   ```")
    
    print("\n5. Run Database Migrations:")
    print("   ```")
    print("   cd Wallet-Backend")
    print("   alembic upgrade head")
    print("   ```")
    
    print("\n6. (Optional) Import Your Data:")
    print("   - Use the exported JSON file to manually recreate your data")
    print("   - Or start fresh with the new Supabase database")

def main():
    print("Wallet App - Supabase Migration Tool")
    print("====================================")
    
    # Check if we can connect to current database
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Connected to current database")
    except Exception as e:
        print(f"✗ Cannot connect to current database: {e}")
        print("Make sure your local PostgreSQL is running and DATABASE_URL is correct")
        return
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Export current data to JSON (recommended)")
    print("2. Show Supabase setup instructions")
    print("3. Both")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        print("\nExporting current data...")
        export_file = export_data_to_json()
        if export_file:
            print(f"✓ Your data has been safely exported to {export_file}")
    
    if choice in ["2", "3"]:
        print_supabase_setup_instructions()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("1. Set up your Supabase project following the instructions above")
    print("2. Update your .env file with Supabase credentials")
    print("3. Run: alembic upgrade head")
    print("4. Test your application with the new database")
    print("="*60)

if __name__ == "__main__":
    main() 