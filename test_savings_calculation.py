"""
Test the savings account calculation logic
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction
from datetime import date

def test_savings_calculation():
    """Test savings starting and final value calculations"""

    print("=== SAVINGS CALCULATION TEST ===")

    transaction_manager = TransactionManager()

    try:
        db = get_db()

        # STEP 1: Get current state and accounts
        print("\n1. CURRENT ACCOUNTS AND BALANCES:")
        accounts = transaction_manager.get_all_accounts()
        for account in accounts:
            print(f"  {account.name}: ${account.running_total:.2f} (default: {account.is_default_save})")

        # STEP 2: Get pay period weeks
        print("\n2. PAY PERIOD WEEKS:")
        weeks = db.query(Week).order_by(Week.week_number).all()
        if len(weeks) >= 2:
            week1_number = weeks[0].week_number
            week2_number = weeks[1].week_number
            print(f"  Week 1: {week1_number}")
            print(f"  Week 2: {week2_number}")
        else:
            print("  Not enough weeks for pay period")
            return

        # STEP 3: Get all transactions for this pay period
        print("\n3. PAY PERIOD TRANSACTIONS:")
        week1_transactions = transaction_manager.get_transactions_by_week(week1_number)
        week2_transactions = transaction_manager.get_transactions_by_week(week2_number)
        pay_period_transactions = week1_transactions + week2_transactions

        print(f"  Total transactions in pay period: {len(pay_period_transactions)}")
        for tx in pay_period_transactions:
            account_info = ""
            if tx.account_id:
                account_info = f" (account_id: {tx.account_id})"
            elif tx.account_saved_to:
                account_info = f" (account_saved_to: {tx.account_saved_to})"
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}{account_info}")

        # STEP 4: Calculate starting and final values for each account
        print("\n4. SAVINGS CALCULATION LOGIC:")
        for account in accounts:
            print(f"\n  --- {account.name} ---")

            # Find transactions for this account during the pay period
            account_transactions = [
                t for t in pay_period_transactions
                if ((t.account_id == account.id) or (t.account_saved_to == account.name))
                and t.is_saving  # Only saving transactions affect account balance
            ]

            print(f"    Transactions affecting this account: {len(account_transactions)}")
            for tx in account_transactions:
                print(f"      Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

            # Calculate period change
            period_change = sum(t.amount for t in account_transactions)
            current_balance = account.running_total
            starting_balance = current_balance - period_change

            print(f"    Current balance: ${current_balance:.2f}")
            print(f"    Period change: ${period_change:.2f}")
            print(f"    Calculated starting balance: ${starting_balance:.2f}")
            print(f"    Final balance: ${current_balance:.2f}")

        # STEP 5: Test your example scenario
        print("\n5. EXAMPLE SCENARIO TEST:")
        print("  Expected behavior:")
        print("    Starting at $10")
        print("    + $50 rollover from Week 2")
        print("    + $40 saved during period")
        print("    = $100 final value")

        # Find the default savings account (where rollovers go)
        default_savings = transaction_manager.get_default_savings_account()
        if default_savings:
            print(f"\n  Testing with {default_savings.name}:")

            # Find transactions for default savings during this period
            default_account_transactions = [
                t for t in pay_period_transactions
                if ((t.account_id == default_savings.id) or (t.account_saved_to == default_savings.name))
                and t.is_saving
            ]

            # Separate rollover vs other savings
            rollover_transactions = [
                t for t in default_account_transactions
                if "end-of-period" in t.description.lower() or "rollover" in t.description.lower()
            ]

            other_savings = [
                t for t in default_account_transactions
                if "end-of-period" not in t.description.lower() and "rollover" not in t.description.lower()
            ]

            rollover_total = sum(t.amount for t in rollover_transactions)
            other_savings_total = sum(t.amount for t in other_savings)
            total_change = sum(t.amount for t in default_account_transactions)

            starting_balance = default_savings.running_total - total_change

            print(f"    Current balance: ${default_savings.running_total:.2f}")
            print(f"    Rollover amount: ${rollover_total:.2f}")
            print(f"    Other savings: ${other_savings_total:.2f}")
            print(f"    Total period change: ${total_change:.2f}")
            print(f"    Calculated starting balance: ${starting_balance:.2f}")
            print(f"    Final balance: ${default_savings.running_total:.2f}")

        # STEP 6: Verification
        print("\n6. VERIFICATION:")
        print("  The logic should show:")
        print("    Starting value = Current balance - Period transactions")
        print("    Final value = Current balance")
        print("    Period change = Rollover + Bill allocations + Direct savings")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    test_savings_calculation()