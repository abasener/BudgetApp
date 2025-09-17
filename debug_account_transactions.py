"""
Debug script to understand account transactions and balances
"""

from services.transaction_manager import TransactionManager
from models import TransactionType

def debug_account_transactions():
    """Debug account transactions to understand balance discrepancies"""

    print("Debugging Account Transactions")
    print("=" * 40)

    transaction_manager = TransactionManager()

    try:
        # Get the specific account with issues
        accounts = transaction_manager.get_all_accounts()
        safety_account = None
        for account in accounts:
            if account.name == "Safety Saving":
                safety_account = account
                break

        if not safety_account:
            print("Safety Saving account not found")
            return

        print(f"Safety Saving Account:")
        print(f"  ID: {safety_account.id}")
        print(f"  Name: {safety_account.name}")
        print(f"  Running Total: ${safety_account.running_total:.2f}")
        print(f"  Is Default Save: {getattr(safety_account, 'is_default_save', False)}")

        print("\\n" + "=" * 40)

        # Get ALL transactions and see which ones might affect this account
        all_transactions = transaction_manager.get_all_transactions()
        print(f"Total transactions in database: {len(all_transactions)}")

        # Filter by different criteria to see what we find
        print("\\nSearching for transactions affecting Safety Saving account...")

        # Method 1: Saving transactions with account_id
        saving_with_id = [
            t for t in all_transactions
            if t.transaction_type == TransactionType.SAVING.value and
               hasattr(t, 'account_id') and t.account_id == safety_account.id
        ]
        print(f"\\n1. Saving transactions with account_id={safety_account.id}: {len(saving_with_id)}")
        for tx in saving_with_id:
            print(f"   - {tx.date}: ${tx.amount:.2f} - {tx.description}")

        # Method 2: Saving transactions with account_saved_to
        saving_with_name = [
            t for t in all_transactions
            if t.transaction_type == TransactionType.SAVING.value and
               hasattr(t, 'account_saved_to') and t.account_saved_to == safety_account.name
        ]
        print(f"\\n2. Saving transactions with account_saved_to='{safety_account.name}': {len(saving_with_name)}")
        for tx in saving_with_name:
            print(f"   - {tx.date}: ${tx.amount:.2f} - {tx.description}")

        # Method 3: Any transactions mentioning this account by ID
        any_with_id = [
            t for t in all_transactions
            if hasattr(t, 'account_id') and t.account_id == safety_account.id
        ]
        print(f"\\n3. ANY transactions with account_id={safety_account.id}: {len(any_with_id)}")
        for tx in any_with_id:
            print(f"   - {tx.date}: ${tx.amount:.2f} - {tx.transaction_type} - {tx.description}")

        # Method 4: Any transactions mentioning this account by name
        any_with_name = [
            t for t in all_transactions
            if (hasattr(t, 'account_saved_to') and t.account_saved_to == safety_account.name)
        ]
        print(f"\\n4. ANY transactions with account_saved_to='{safety_account.name}': {len(any_with_name)}")
        for tx in any_with_name:
            print(f"   - {tx.date}: ${tx.amount:.2f} - {tx.transaction_type} - {tx.description}")

        # Method 5: Check for rollover transactions to savings
        rollover_to_savings = [
            t for t in all_transactions
            if (t.transaction_type == TransactionType.SAVING.value and
                t.description and "end-of-period surplus" in t.description.lower())
        ]
        print(f"\\n5. Rollover-to-savings transactions: {len(rollover_to_savings)}")
        total_rollover_amount = 0
        for tx in rollover_to_savings:
            print(f"   - {tx.date}: ${tx.amount:.2f} - {tx.description}")
            print(f"     Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"     Account Name: {getattr(tx, 'account_saved_to', 'None')}")
            if hasattr(tx, 'account_id') and tx.account_id == safety_account.id:
                total_rollover_amount += tx.amount

        print(f"\\nTotal rollover amount to Safety Saving: ${total_rollover_amount:.2f}")

        # Method 6: Check all saving transactions to understand where money is going
        all_saving_transactions = [
            t for t in all_transactions
            if t.transaction_type == TransactionType.SAVING.value
        ]
        print(f"\\n6. ALL saving transactions: {len(all_saving_transactions)}")
        for tx in all_saving_transactions:
            print(f"   - {tx.date}: ${tx.amount:.2f} - {tx.description}")
            print(f"     Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"     Account Name: {getattr(tx, 'account_saved_to', 'None')}")

        print("\\n" + "=" * 40)
        print("Debug completed")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    debug_account_transactions()