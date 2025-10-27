"""
Clean all paycheck data, transactions, and weeks for fresh testing
Keep only bills, savings accounts, and categories
"""

from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction

def clean_all_data():
    """Remove all paychecks, transactions, and weeks"""

    print("=== CLEANING ALL PAYCHECK DATA ===")

    transaction_manager = TransactionManager()

    try:
        db = get_db()

        # STEP 1: Remove all transactions
        print("\n1. REMOVING ALL TRANSACTIONS:")
        all_transactions = db.query(Transaction).all()
        print(f"  Found {len(all_transactions)} transactions to remove")
        for tx in all_transactions:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")
            db.delete(tx)

        db.commit()
        print("  All transactions removed")

        # STEP 2: Remove all weeks
        print("\n2. REMOVING ALL WEEKS:")
        all_weeks = db.query(Week).all()
        print(f"  Found {len(all_weeks)} weeks to remove")
        for week in all_weeks:
            print(f"    Week {week.week_number}: {week.start_date} to {week.end_date}")
            db.delete(week)

        db.commit()
        print("  All weeks removed")

        # STEP 3: Reset bill running totals to 0
        print("\n3. RESETTING BILL BALANCES:")
        bills = transaction_manager.get_all_bills()
        for bill in bills:
            old_total = bill.running_total
            bill.running_total = 0.0
            print(f"  {bill.name}: ${old_total:.2f} -> $0.00")

        db.commit()
        print("  All bill balances reset")

        # STEP 4: Reset savings account balances and balance history to 0
        print("\n4. RESETTING SAVINGS ACCOUNT BALANCES AND HISTORY:")
        accounts = transaction_manager.get_all_accounts()
        for account in accounts:
            old_total = account.running_total
            old_history_length = len(account.balance_history) if account.balance_history else 0

            # Reset running total
            account.running_total = 0.0

            # Reset balance history to start fresh with 0 (direct assignment is more reliable)
            account.balance_history = [0.0]

            print(f"  {account.name}: ${old_total:.2f} -> $0.00 (history: {old_history_length} entries -> 1 entry)")

        db.commit()
        print("  All savings account balances and histories reset")

        # STEP 5: Verify clean state
        print("\n5. VERIFICATION:")
        remaining_transactions = db.query(Transaction).count()
        remaining_weeks = db.query(Week).count()
        print(f"  Transactions remaining: {remaining_transactions}")
        print(f"  Weeks remaining: {remaining_weeks}")
        print(f"  Bills: {len(bills)} (preserved)")
        print(f"  Savings accounts: {len(accounts)} (preserved)")

        if remaining_transactions == 0 and remaining_weeks == 0:
            print("  ✅ Data successfully cleaned - ready for fresh testing!")
        else:
            print("  ❌ Cleanup incomplete")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    clean_all_data()