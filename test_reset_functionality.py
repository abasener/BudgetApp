"""
Test the Reset Test Data functionality to ensure it properly cleans everything
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor

def test_reset_functionality():
    """Test that reset functionality works properly"""

    print("=== TESTING RESET FUNCTIONALITY ===")

    tm = TransactionManager()
    pp = PaycheckProcessor()

    try:
        # Check current state
        print("\n1. CURRENT STATE:")
        from models import Transaction, Week, Account, Bill

        transactions = tm.db.query(Transaction).all()
        weeks = tm.db.query(Week).all()
        accounts = tm.db.query(Account).all()
        bills = tm.db.query(Bill).all()

        print(f"   Transactions: {len(transactions)}")
        print(f"   Weeks: {len(weeks)}")
        print(f"   Accounts: {len(accounts)}")
        print(f"   Bills: {len(bills)}")

        # Show account details
        print("\n2. ACCOUNT DETAILS:")
        for account in accounts:
            history = account.get_balance_history_copy() if hasattr(account, 'get_balance_history_copy') else account.balance_history
            print(f"   {account.name}: balance=${account.running_total:.2f}, history={history}")

        # Show bill details
        print("\n3. BILL DETAILS:")
        for bill in bills:
            print(f"   {bill.name}: balance=${bill.running_total:.2f}")

        # Simulate the reset test data process (same as in settings dialog)
        print("\n4. SIMULATING RESET TEST DATA...")

        # Delete transactions and weeks
        transaction_count = tm.db.query(Transaction).count()
        week_count = tm.db.query(Week).count()

        tm.db.query(Transaction).delete()
        tm.db.query(Week).delete()

        # Reset account balances and histories
        updated_accounts = tm.db.query(Account).all()
        for account in updated_accounts:
            old_balance = account.running_total
            account.running_total = 0.0
            account.balance_history = [0.0]
            print(f"   Reset {account.name}: ${old_balance:.2f} -> $0.00")

        # Reset bill balances
        updated_bills = tm.db.query(Bill).all()
        for bill in updated_bills:
            old_balance = bill.running_total
            bill.running_total = 0.0
            print(f"   Reset {bill.name}: ${old_balance:.2f} -> $0.00")

        tm.db.commit()
        print(f"   Deleted {transaction_count} transactions and {week_count} weeks")

        # Verify clean state
        print("\n5. VERIFICATION AFTER RESET:")
        remaining_transactions = tm.db.query(Transaction).count()
        remaining_weeks = tm.db.query(Week).count()

        print(f"   Remaining transactions: {remaining_transactions}")
        print(f"   Remaining weeks: {remaining_weeks}")

        final_accounts = tm.db.query(Account).all()
        print("   Account states:")
        for account in final_accounts:
            history = account.get_balance_history_copy() if hasattr(account, 'get_balance_history_copy') else account.balance_history
            print(f"     {account.name}: balance=${account.running_total:.2f}, history={history}")

        final_bills = tm.db.query(Bill).all()
        print("   Bill states:")
        for bill in final_bills:
            print(f"     {bill.name}: balance=${bill.running_total:.2f}")

        # Test adding a simple paycheck to fresh state
        print("\n6. TESTING FRESH PAYCHECK PROCESSING:")
        from datetime import date

        paycheck_amount = 1500.0
        paycheck_date = date.today()
        week_start_date = date.today()

        print(f"   Adding paycheck: ${paycheck_amount:.2f}")
        split = pp.process_new_paycheck(paycheck_amount, paycheck_date, week_start_date)

        print(f"   Bills deducted: ${split.bills_deducted:.2f}")
        print(f"   Week 1 allocation: ${split.week1_allocation:.2f}")
        print(f"   Week 2 allocation: ${split.week2_allocation:.2f}")

        # Check final account states
        final_accounts_after_paycheck = tm.db.query(Account).all()
        print("\n7. ACCOUNT STATES AFTER PAYCHECK:")
        for account in final_accounts_after_paycheck:
            history = account.get_balance_history_copy() if hasattr(account, 'get_balance_history_copy') else account.balance_history
            print(f"   {account.name}: balance=${account.running_total:.2f}, history={history}")

        # The savings account history should now be [0.0] (starting from clean state)
        default_savings = tm.get_default_savings_account()
        if default_savings:
            print(f"\n8. DEFAULT SAVINGS VERIFICATION:")
            print(f"   Balance: ${default_savings.running_total:.2f}")
            print(f"   History: {default_savings.get_balance_history_copy()}")

            if default_savings.get_balance_history_copy() == [0.0]:
                print("   ✅ Balance history properly reset!")
            else:
                print("   ❌ Balance history not properly reset!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pp.close()
        tm.close()

if __name__ == "__main__":
    test_reset_functionality()