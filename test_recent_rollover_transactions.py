"""
Test script to check recent rollover transactions to savings accounts
"""

from services.transaction_manager import TransactionManager
from models import TransactionType
from datetime import date, timedelta

def test_recent_rollover_transactions():
    """Check recent rollover transactions to see if they're properly tracked"""

    print("Checking Recent Rollover Transactions")
    print("=" * 40)

    transaction_manager = TransactionManager()

    try:
        # Get the default savings account
        default_savings = transaction_manager.get_default_savings_account()
        print(f"Default Savings Account: {default_savings.name} (ID: {default_savings.id})")
        print(f"Current Balance: ${default_savings.running_total:.2f}")

        # Get all recent transactions (last 7 days)
        recent_date = date.today() - timedelta(days=7)
        all_transactions = transaction_manager.get_all_transactions()
        recent_transactions = [t for t in all_transactions if t.date >= recent_date]

        print(f"\\nRecent transactions (last 7 days): {len(recent_transactions)}")

        # Look for rollover transactions to savings
        rollover_transactions = [
            t for t in recent_transactions
            if (t.transaction_type == TransactionType.SAVING.value and
                t.description and "end-of-period surplus" in t.description.lower())
        ]

        print(f"\\nRollover-to-savings transactions: {len(rollover_transactions)}")
        for tx in rollover_transactions:
            print(f"  - {tx.date}: ${tx.amount:.2f}")
            print(f"    Description: {tx.description}")
            print(f"    Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"    Account Name: {getattr(tx, 'account_saved_to', 'None')}")
            print(f"    Week Number: {tx.week_number}")

        # Check all saving transactions to the default account
        account_saving_transactions = [
            t for t in recent_transactions
            if (t.transaction_type == TransactionType.SAVING.value and
                ((hasattr(t, 'account_id') and t.account_id == default_savings.id) or
                 (hasattr(t, 'account_saved_to') and t.account_saved_to == default_savings.name)))
        ]

        print(f"\\nAll saving transactions to '{default_savings.name}': {len(account_saving_transactions)}")
        for tx in account_saving_transactions:
            print(f"  - {tx.date}: ${tx.amount:.2f} - {tx.description}")
            print(f"    Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"    Account Name: {getattr(tx, 'account_saved_to', 'None')}")

        print("\\n" + "=" * 40)
        print("Rollover transaction check completed")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    test_recent_rollover_transactions()