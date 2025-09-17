"""
Test the fixed savings calculation logic
"""

from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction

def test_savings_fix():
    """Test that the savings calculation no longer shows 'error loading data'"""

    print("=== SAVINGS FIX TEST ===")

    transaction_manager = TransactionManager()

    try:
        db = get_db()

        # STEP 1: Simulate the logic from update_savings_values
        print("\n1. TESTING WEEK DETECTION LOGIC:")

        # Get all weeks and find the most recent complete pay period
        all_weeks = transaction_manager.get_all_weeks()
        print(f"  Found {len(all_weeks)} weeks total")

        current_pay_period_weeks = []
        if len(all_weeks) >= 2:
            # Sort by week number and take the two most recent
            sorted_weeks = sorted(all_weeks, key=lambda w: w.week_number, reverse=True)
            current_pay_period_weeks = [sorted_weeks[1].week_number, sorted_weeks[0].week_number]
            print(f"  Current pay period weeks: {current_pay_period_weeks}")
        else:
            print("  Not enough weeks for pay period")

        # STEP 2: Test transaction retrieval
        print("\n2. TESTING TRANSACTION RETRIEVAL:")
        pay_period_transactions = []
        if len(current_pay_period_weeks) == 2:
            week1_transactions = transaction_manager.get_transactions_by_week(current_pay_period_weeks[0])
            week2_transactions = transaction_manager.get_transactions_by_week(current_pay_period_weeks[1])
            pay_period_transactions = week1_transactions + week2_transactions
            print(f"  Week {current_pay_period_weeks[0]} transactions: {len(week1_transactions)}")
            print(f"  Week {current_pay_period_weeks[1]} transactions: {len(week2_transactions)}")
            print(f"  Total pay period transactions: {len(pay_period_transactions)}")

        # STEP 3: Test account calculation
        print("\n3. TESTING ACCOUNT CALCULATIONS:")
        accounts = transaction_manager.get_all_accounts()

        for account in accounts:
            print(f"\n  --- {account.name} ---")

            # Calculate transactions for this account during the current pay period
            account_transactions = [
                t for t in pay_period_transactions
                if ((t.account_id == account.id) or (t.account_saved_to == account.name))
                and t.is_saving  # Only saving transactions affect account balance
            ]

            print(f"    Account transactions: {len(account_transactions)}")
            for tx in account_transactions:
                print(f"      Week {tx.week_number}: ${tx.amount:.2f} - {tx.description}")

            # Sum up transactions for this period
            period_change = sum(t.amount for t in account_transactions)

            # Historical calculation logic:
            current_balance = account.running_total  # k_final_value
            starting_balance = current_balance - period_change  # k_starting_value

            print(f"    Current balance (final): ${current_balance:.2f}")
            print(f"    Period change: ${period_change:.2f}")
            print(f"    Starting balance: ${starting_balance:.2f}")

        # STEP 4: Test the formatted output
        print("\n4. TESTING FORMATTED OUTPUT:")
        start_account_text = ""
        final_account_text = ""

        for account in accounts:
            name = account.name[:14] + "..." if len(account.name) > 14 else account.name

            # Calculate the same way as the fixed method
            account_transactions = [
                t for t in pay_period_transactions
                if ((t.account_id == account.id) or (t.account_saved_to == account.name))
                and t.is_saving
            ]

            period_change = sum(t.amount for t in account_transactions)
            current_balance = account.running_total
            starting_balance = current_balance - period_change

            # Format display
            start_amount_str = f"${starting_balance:.0f}"
            final_amount_str = f"${current_balance:.0f}"

            start_account_text += f"{name:<16} {start_amount_str:>10}\n"
            final_account_text += f"{name:<16} {final_amount_str:>10}\n"

        print("  Starting Savings Display:")
        print(start_account_text or "No accounts")

        print("  Final Savings Display:")
        print(final_account_text or "No accounts")

        # STEP 5: Verify no errors
        print("\n5. ERROR CHECK:")
        if start_account_text and final_account_text:
            print("  SUCCESS: No 'error loading data' - calculations completed")
        else:
            print("  WARNING: Empty display text (but no error)")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    test_savings_fix()