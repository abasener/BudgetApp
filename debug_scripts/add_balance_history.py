"""
Migration: Add balance_history column to existing accounts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import get_db, Account
from sqlalchemy import text

def migrate_add_balance_history():
    """Add balance_history column to existing accounts and initialize with current balance"""

    print("=== ADDING BALANCE HISTORY TO ACCOUNTS ===")

    db = get_db()

    try:
        # First, check if the column already exists
        try:
            result = db.execute(text("SELECT balance_history FROM accounts LIMIT 1"))
            print("Balance history column already exists, skipping column creation")
        except Exception:
            # Column doesn't exist, add it
            print("Adding balance_history column to accounts table...")
            db.execute(text("ALTER TABLE accounts ADD COLUMN balance_history JSON DEFAULT '[]'"))
            db.commit()
            print("Successfully added balance_history column")

        # Initialize balance history for all existing accounts
        print("Initializing balance history for existing accounts...")

        accounts = db.query(Account).all()
        updated_count = 0

        for account in accounts:
            # Check if balance_history is null or empty
            if account.balance_history is None or len(account.balance_history) == 0:
                # Initialize with current running_total
                account.initialize_balance_history(account.running_total)
                updated_count += 1
                print(f"  Initialized {account.name}: [{account.running_total:.2f}]")
            else:
                print(f"  Skipped {account.name}: already has {len(account.balance_history)} history entries")

        if updated_count > 0:
            db.commit()
            print(f"Successfully initialized balance history for {updated_count} accounts")
        else:
            print("No accounts needed initialization")

        # Verify the migration
        print("\nVerification:")
        accounts = db.query(Account).all()
        for account in accounts:
            history = account.get_balance_history_copy()
            print(f"  {account.name}: {len(history)} entries, current: ${account.running_total:.2f}")

        print("Migration completed successfully!")

    except Exception as e:
        print(f"ERROR during migration: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_balance_history()