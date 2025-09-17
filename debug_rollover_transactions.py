"""
Debug script to find rollover transactions to savings accounts
"""

from services.transaction_manager import TransactionManager
from models import TransactionType

def debug_rollover_transactions():
    """Debug rollover transactions to understand savings account balances"""

    print("Debugging Rollover Transactions to Savings")
    print("=" * 45)

    transaction_manager = TransactionManager()

    try:
        # Get the default savings account
        default_savings = transaction_manager.get_default_savings_account()
        if not default_savings:
            print("No default savings account found")
            return

        print(f"Default Savings Account:")
        print(f"  ID: {default_savings.id}")
        print(f"  Name: {default_savings.name}")
        print(f"  Running Total: ${default_savings.running_total:.2f}")

        print("\\n" + "=" * 45)

        # Get all transactions
        all_transactions = transaction_manager.get_all_transactions()

        # Look for rollover transactions to savings (end-of-period surplus)
        rollover_savings_transactions = [
            t for t in all_transactions
            if (t.transaction_type == TransactionType.SAVING.value and
                t.description and "end-of-period surplus" in t.description.lower())
        ]

        print(f"Rollover-to-savings transactions: {len(rollover_savings_transactions)}")
        total_rollover = 0
        for tx in rollover_savings_transactions:
            print(f"  - {tx.date}: ${tx.amount:.2f} - {tx.description}")
            print(f"    Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"    Account Name: {getattr(tx, 'account_saved_to', 'None')}")
            total_rollover += tx.amount

        print(f"\\nTotal rollover amount: ${total_rollover:.2f}")

        # Also look for any transactions with the default savings account ID
        account_transactions = [
            t for t in all_transactions
            if (hasattr(t, 'account_id') and t.account_id == default_savings.id)
        ]

        print(f"\\nTransactions with account_id={default_savings.id}: {len(account_transactions)}")
        for tx in account_transactions:
            print(f"  - {tx.date}: ${tx.amount:.2f} - {tx.transaction_type} - {tx.description}")

        # Look for transactions with account name
        name_transactions = [
            t for t in all_transactions
            if (hasattr(t, 'account_saved_to') and t.account_saved_to == default_savings.name)
        ]

        print(f"\\nTransactions with account_saved_to='{default_savings.name}': {len(name_transactions)}")
        for tx in name_transactions:
            print(f"  - {tx.date}: ${tx.amount:.2f} - {tx.transaction_type} - {tx.description}")

        # Calculate total of transactions that should affect this account
        account_total = sum(tx.amount for tx in account_transactions) + sum(tx.amount for tx in name_transactions)
        print(f"\\nTotal from transactions: ${account_total:.2f}")
        print(f"Account balance: ${default_savings.running_total:.2f}")
        print(f"Difference: ${default_savings.running_total - account_total:.2f}")

        print("\\n" + "=" * 45)
        print("Debug completed")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    debug_rollover_transactions()