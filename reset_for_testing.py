"""
Reset database for testing - remove transactions and weeks, keep accounts/bills/categories
"""

from models import get_db, Week, Transaction, Account, Bill
from services.transaction_manager import TransactionManager

def reset_for_testing():
    """Remove all transactions and weeks while keeping accounts, bills, and categories"""

    print("=== RESETTING DATABASE FOR TESTING ===")

    transaction_manager = TransactionManager()

    try:
        db = transaction_manager.db

        # Count before deletion
        week_count = db.query(Week).count()
        transaction_count = db.query(Transaction).count()
        account_count = db.query(Account).count()
        bill_count = db.query(Bill).count()

        print(f"\nBefore deletion:")
        print(f"  Weeks: {week_count}")
        print(f"  Transactions: {transaction_count}")
        print(f"  Accounts: {account_count}")
        print(f"  Bills: {bill_count}")

        # Delete all transactions
        print(f"\nDeleting {transaction_count} transactions...")
        db.query(Transaction).delete()

        # Delete all weeks
        print(f"Deleting {week_count} weeks...")
        db.query(Week).delete()

        # Reset account balances to 0 and clear balance history
        print("\nResetting account balances to $0...")
        accounts = db.query(Account).all()
        for account in accounts:
            old_balance = account.running_total
            account.running_total = 0.0
            account.balance_history = []  # Clear balance history
            print(f"  {account.name}: ${old_balance:.2f} -> $0.00 (history cleared)")

        # Commit changes
        db.commit()

        # Verify deletion
        week_count_after = db.query(Week).count()
        transaction_count_after = db.query(Transaction).count()
        account_count_after = db.query(Account).count()
        bill_count_after = db.query(Bill).count()
        print(f"\nAfter deletion:")
        print(f"  Weeks: {week_count_after}")
        print(f"  Transactions: {transaction_count_after}")
        print(f"  Accounts: {account_count_after}")
        print(f"  Bills: {bill_count_after}")

        print(f"\nSUCCESS: Successfully reset database for testing!")
        print(f"SUCCESS: Kept {account_count_after} accounts and {bill_count_after} bills")
        print(f"SUCCESS: Removed {week_count} weeks and {transaction_count} transactions")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    reset_for_testing()