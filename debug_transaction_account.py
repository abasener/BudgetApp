"""
Debug transaction account linking
"""

from services.transaction_manager import TransactionManager

def debug_transaction_account():
    """Check if rollover transaction has account_id set"""

    print("=== DEBUG TRANSACTION ACCOUNT LINKING ===")

    tm = TransactionManager()

    try:
        # Get all transactions with detailed info
        all_transactions = tm.get_all_transactions()

        print(f"\nTransactions with account details:")
        for tx in all_transactions:
            account_name = "None"
            if hasattr(tx, 'account_id') and tx.account_id:
                account = tm.get_account_by_id(tx.account_id)
                if account:
                    account_name = account.name
            print(f"  {tx.id}: Week {tx.week_number}, {tx.transaction_type}, ${tx.amount:.2f}")
            print(f"      Description: {tx.description}")
            print(f"      Account ID: {getattr(tx, 'account_id', 'No attribute')}")
            print(f"      Account Name: {account_name}")
            print()

        # Check the specific rollover transaction
        rollover_tx = None
        for tx in all_transactions:
            if "End-of-period deficit from Week 2" in tx.description:
                rollover_tx = tx
                break

        if rollover_tx:
            print(f"Rollover transaction details:")
            print(f"  ID: {rollover_tx.id}")
            print(f"  Type: {rollover_tx.transaction_type}")
            print(f"  Amount: ${rollover_tx.amount:.2f}")
            print(f"  Account ID: {getattr(rollover_tx, 'account_id', 'No attribute')}")

            if hasattr(rollover_tx, 'account_id') and rollover_tx.account_id:
                account = tm.get_account_by_id(rollover_tx.account_id)
                if account:
                    print(f"  Account: {account.name}")
                    print(f"  Account balance: ${account.running_total:.2f}")
                    print(f"  Should this transaction update the account? YES")
                else:
                    print(f"  Account: Not found for ID {rollover_tx.account_id}")
            else:
                print(f"  Account: No account_id set - THIS IS THE PROBLEM!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_transaction_account()