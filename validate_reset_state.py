"""
Validate the current database state after reset test data button was used
"""

from services.transaction_manager import TransactionManager
from models import Transaction, Week, Account, Bill

def validate_reset_state():
    """Validate that the database is in a clean state ready for test data"""

    tm = TransactionManager()

    try:
        print('=== DATABASE STATE VALIDATION ===')

        # Check transactions
        transactions = tm.db.query(Transaction).all()
        print(f'\nTransactions: {len(transactions)}')
        if transactions:
            print('  WARNING: Transactions still exist!')
            for tx in transactions[:5]:  # Show first 5
                print(f'    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}')
            if len(transactions) > 5:
                print(f'    ... and {len(transactions) - 5} more')
        else:
            print('  [OK] All transactions deleted')

        # Check weeks
        weeks = tm.db.query(Week).all()
        print(f'\nWeeks: {len(weeks)}')
        if weeks:
            print('  WARNING: Weeks still exist!')
            for week in weeks[:5]:  # Show first 5
                print(f'    Week {week.week_number}: ${week.running_total:.2f} ({week.start_date} to {week.end_date})')
            if len(weeks) > 5:
                print(f'    ... and {len(weeks) - 5} more')
        else:
            print('  [OK] All weeks deleted')

        # Check accounts
        accounts = tm.db.query(Account).all()
        print(f'\nAccounts: {len(accounts)}')
        for account in accounts:
            history = account.get_balance_history_copy()
            print(f'  {account.name}:')
            print(f'    Balance: ${account.running_total:.2f}')
            print(f'    History: {history}')
            print(f'    History length: {len(history)}')
            print(f'    Goal: ${account.goal_amount:.2f}')
            print(f'    Auto-save: ${account.auto_save_amount:.2f}')
            print(f'    Default savings: {account.is_default_save}')

        # Check bills
        bills = tm.db.query(Bill).all()
        print(f'\nBills: {len(bills)}')
        for bill in bills:
            print(f'  {bill.name}:')
            print(f'    Balance: ${bill.running_total:.2f}')
            print(f'    Amount to save: ${bill.amount_to_save:.2f}')
            print(f'    Type: {bill.bill_type}')

        # Check if Safety Saving starting value was changed
        safety_saving = None
        for account in accounts:
            if 'safety' in account.name.lower():
                safety_saving = account
                break

        if safety_saving:
            print(f'\n=== SAFETY SAVINGS ANALYSIS ===')
            print(f'Name: {safety_saving.name}')
            print(f'Current balance: ${safety_saving.running_total:.2f}')
            print(f'Balance history: {safety_saving.get_balance_history_copy()}')

            # Validate the setup
            history = safety_saving.get_balance_history_copy()
            if len(history) == 1 and history[0] == safety_saving.running_total:
                print('[OK] Starting value properly set - balance matches history[0]')
            elif len(history) == 1 and history[0] != safety_saving.running_total:
                print(f'[WARNING] Mismatch: balance=${safety_saving.running_total:.2f} but history[0]=${history[0]:.2f}')
            else:
                print(f'[WARNING] History has {len(history)} entries, expected 1 for fresh start')

        print(f'\n=== OVERALL VALIDATION ===')
        is_clean = len(transactions) == 0 and len(weeks) == 0
        if is_clean:
            print('[OK] Database is clean - ready for test data import')
        else:
            print('[ERROR] Database is NOT clean - reset may not have worked properly')

        # Check for any stale data that might cause issues
        total_account_balance = sum(acc.running_total for acc in accounts)
        total_bill_balance = sum(bill.running_total for bill in bills)

        print(f'\nTotal money in accounts: ${total_account_balance:.2f}')
        print(f'Total money in bills: ${total_bill_balance:.2f}')

        # Specific checks for readiness
        print(f'\n=== READINESS CHECKLIST ===')

        # 1. No old transactions/weeks
        clean_data = len(transactions) == 0 and len(weeks) == 0
        print(f'1. Clean data (no old transactions/weeks): {"YES" if clean_data else "NO"}')

        # 2. All bills at $0
        bills_reset = all(bill.running_total == 0.0 for bill in bills)
        print(f'2. All bills reset to $0: {"YES" if bills_reset else "NO"}')

        # 3. All accounts have proper history
        accounts_proper_history = all(len(acc.get_balance_history_copy()) == 1 for acc in accounts)
        print(f'3. All accounts have single history entry: {"YES" if accounts_proper_history else "NO"}')

        # 4. Balance matches history for all accounts
        balance_history_match = all(acc.running_total == acc.get_balance_history_copy()[0] for acc in accounts if acc.get_balance_history_copy())
        print(f'4. Balance matches history[0] for all accounts: {"YES" if balance_history_match else "NO"}')

        # Overall readiness
        ready = clean_data and bills_reset and accounts_proper_history and balance_history_match
        print(f'\n=== FINAL VERDICT ===')
        print(f'Ready for test data import: {"YES - GO AHEAD!" if ready else "NO - ISSUES FOUND"}')

        if not ready:
            print('\nIssues to fix:')
            if not clean_data:
                print('- Old transactions/weeks still exist')
            if not bills_reset:
                print('- Some bills have non-zero balances')
            if not accounts_proper_history:
                print('- Some accounts have incorrect history length')
            if not balance_history_match:
                print('- Some accounts have balance/history mismatch')

    finally:
        tm.close()

if __name__ == "__main__":
    validate_reset_state()