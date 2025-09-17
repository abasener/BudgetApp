"""
Debug all recent transactions to understand what's happening
"""

from services.transaction_manager import TransactionManager
from datetime import date, timedelta

def debug_all_recent_transactions():
    """Debug all recent transactions"""

    print("Debugging All Recent Transactions")
    print("=" * 40)

    transaction_manager = TransactionManager()

    try:
        # Get all recent transactions (last 3 days)
        recent_date = date.today() - timedelta(days=3)
        all_transactions = transaction_manager.get_all_transactions()
        recent_transactions = [t for t in all_transactions if t.date >= recent_date]

        print(f"All recent transactions (last 3 days): {len(recent_transactions)}")

        for tx in recent_transactions:
            print(f"\\n- {tx.date}: ${tx.amount:.2f}")
            print(f"  Type: {tx.transaction_type}")
            print(f"  Description: {tx.description}")
            print(f"  Week: {tx.week_number}")
            print(f"  Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"  Account Name: {getattr(tx, 'account_saved_to', 'None')}")
            print(f"  Bill ID: {getattr(tx, 'bill_id', 'None')}")

        # Check specifically for today's transactions
        today_transactions = [t for t in all_transactions if t.date == date.today()]
        print(f"\\nToday's transactions: {len(today_transactions)}")

        for tx in today_transactions:
            print(f"\\n- TODAY {tx.date}: ${tx.amount:.2f}")
            print(f"  Type: {tx.transaction_type}")
            print(f"  Description: {tx.description}")
            print(f"  Week: {tx.week_number}")
            print(f"  Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"  Account Name: {getattr(tx, 'account_saved_to', 'None')}")

        print("\\n" + "=" * 40)
        print("Debug completed")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    debug_all_recent_transactions()