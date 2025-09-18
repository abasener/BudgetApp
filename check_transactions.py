"""
Check what transactions were created during testing
"""

from services.transaction_manager import TransactionManager

def check_transactions():
    """Check what transactions were created"""

    print("=== CHECKING TRANSACTIONS ===")

    tm = TransactionManager()

    try:
        # Get all transactions
        all_transactions = tm.get_all_transactions()
        print(f"\nTotal transactions: {len(all_transactions)}")

        for tx in all_transactions:
            print(f"  Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")
            if hasattr(tx, 'account_id') and tx.account_id:
                account = tm.get_account_by_id(tx.account_id)
                if account:
                    print(f"    -> Account: {account.name}")

        # Check specific rollover transactions
        rollover_txs = [tx for tx in all_transactions if 'rollover' in tx.description.lower() or 'surplus' in tx.description.lower() or 'deficit' in tx.description.lower()]
        print(f"\nRollover transactions: {len(rollover_txs)}")
        for tx in rollover_txs:
            print(f"  Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")
            if hasattr(tx, 'account_id') and tx.account_id:
                account = tm.get_account_by_id(tx.account_id)
                if account:
                    print(f"    -> Account: {account.name}")

        # Check account balances
        print(f"\nAccount balances:")
        accounts = tm.get_all_accounts()
        for account in accounts:
            print(f"  {account.name}: ${account.running_total:.2f}")
            print(f"    History: {account.get_balance_history_copy()}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    check_transactions()