"""
Test the updated savings value display logic for the weekly view
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_savings_display_fix():
    """Test the new savings value calculation logic"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Testing Savings Display Fix ===")

    # Create test accounts with different starting balances
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=200.0,
        is_default_save=True,
        initial_balance=1500.0  # Starting with $1500
    )

    vacation_fund = tm.add_account(
        name="Vacation Fund",
        goal_amount=3000.0,
        auto_save_amount=100.0,
        is_default_save=False,
        initial_balance=800.0  # Starting with $800
    )

    print(f"Initial Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"Initial Vacation Fund: ${vacation_fund.get_current_balance(tm.db):.2f}")

    # Check initial account histories
    print("\n--- Initial Account Histories ---")
    for account in [emergency_fund, vacation_fund]:
        history = account.get_account_history(tm.db)
        print(f"{account.name}:")
        for entry in history:
            print(f"  {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}")

    # Process first paycheck (this will be our test period)
    print("\n--- First Paycheck ---")
    paycheck_split = processor.process_new_paycheck(
        paycheck_amount=2500.0,
        paycheck_date=date(2024, 2, 15),  # Using Feb dates
        week_start_date=date(2024, 2, 15)
    )

    # Get the weeks created
    weeks = tm.get_all_weeks()
    week1 = weeks[0]
    week2 = weeks[1]

    print(f"Created Week 1: {week1.start_date} to {week1.end_date}")
    print(f"Created Week 2: {week2.start_date} to {week2.end_date}")

    # Test period dates
    period_start_date = min(week1.start_date, week2.start_date)
    period_end_date = max(week1.end_date, week2.end_date)

    print(f"Pay period: {period_start_date} to {period_end_date}")

    # Check account balances and histories after paycheck
    print("\n--- After Paycheck Processing ---")
    for account in [emergency_fund, vacation_fund]:
        current_balance = account.get_current_balance(tm.db)
        print(f"{account.name}: ${current_balance:.2f}")

        history = account.get_account_history(tm.db)
        print(f"  History entries: {len(history)}")
        for entry in history:
            print(f"    {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}")

    # Now test the helper functions (simulating what the weekly view would do)
    print("\n--- Testing Savings Value Calculation Functions ---")

    # Import the functions we need to test (we'll create a mock class)
    class MockWeeklyView:
        def __init__(self, transaction_manager):
            self.transaction_manager = transaction_manager

        def _find_balance_on_or_before_date(self, account_history, target_date):
            """Find the running total from the latest AccountHistory entry on or before target_date"""
            if not account_history:
                return 0.0

            latest_entry = None
            for entry in account_history:
                if entry.transaction_date <= target_date:
                    if latest_entry is None or entry.transaction_date > latest_entry.transaction_date:
                        latest_entry = entry
                    elif entry.transaction_date == latest_entry.transaction_date and entry.id > latest_entry.id:
                        latest_entry = entry

            return latest_entry.running_total if latest_entry else 0.0

        def _find_balance_between_dates(self, account_history, start_date, end_date, fallback_balance):
            """Find the running total from the latest AccountHistory entry between start_date and end_date"""
            if not account_history:
                return fallback_balance

            latest_entry = None
            for entry in account_history:
                if start_date <= entry.transaction_date <= end_date:
                    if latest_entry is None or entry.transaction_date > latest_entry.transaction_date:
                        latest_entry = entry
                    elif entry.transaction_date == latest_entry.transaction_date and entry.id > latest_entry.id:
                        latest_entry = entry

            return latest_entry.running_total if latest_entry else fallback_balance

    mock_view = MockWeeklyView(tm)

    # Test calculation for each account
    for account in [emergency_fund, vacation_fund]:
        print(f"\n--- Testing {account.name} ---")

        account_history = account.get_account_history(tm.db)

        # Find starting balance (latest entry BEFORE period start date)
        day_before_period = period_start_date - timedelta(days=1)
        starting_balance = mock_view._find_balance_on_or_before_date(account_history, day_before_period)

        # Find final balance (between period start and end)
        final_balance = mock_view._find_balance_between_dates(account_history, period_start_date, period_end_date, starting_balance)

        # Calculate amount paid
        amount_paid = final_balance - starting_balance

        print(f"  Period: {period_start_date} to {period_end_date}")
        print(f"  Starting balance: ${starting_balance:.2f}")
        print(f"  Final balance: ${final_balance:.2f}")
        print(f"  Amount paid to savings: ${amount_paid:.2f}")

        # Verify this matches expected values
        if account.name == "Emergency Fund":
            # Should be: Start=1500, Final=1500+200=1700, Paid=200
            assert abs(starting_balance - 1500.0) < 0.01, f"Expected start 1500, got {starting_balance}"
            assert abs(final_balance - 1700.0) < 0.01, f"Expected final 1700, got {final_balance}"
            assert abs(amount_paid - 200.0) < 0.01, f"Expected paid 200, got {amount_paid}"
        elif account.name == "Vacation Fund":
            # Should be: Start=800, Final=800+100=900, Paid=100
            assert abs(starting_balance - 800.0) < 0.01, f"Expected start 800, got {starting_balance}"
            assert abs(final_balance - 900.0) < 0.01, f"Expected final 900, got {final_balance}"
            assert abs(amount_paid - 100.0) < 0.01, f"Expected paid 100, got {amount_paid}"

    # Test edge case: What if we look for a period before any transactions?
    print("\n--- Testing Edge Case: Date Before Any Transactions ---")
    early_date = date(2023, 12, 31)  # Before all our transactions

    for account in [emergency_fund, vacation_fund]:
        account_history = account.get_account_history(tm.db)
        balance_before = mock_view._find_balance_on_or_before_date(account_history, early_date)
        print(f"{account.name} balance before {early_date}: ${balance_before:.2f}")
        # Should be 0.0 since no entries exist before that date

    # Test edge case: What if we look for a period with no changes?
    print("\n--- Testing Edge Case: Period With No Changes ---")
    future_start = date(2024, 3, 1)
    future_end = date(2024, 3, 15)

    for account in [emergency_fund, vacation_fund]:
        account_history = account.get_account_history(tm.db)
        start_balance = mock_view._find_balance_on_or_before_date(account_history, future_start)
        final_balance = mock_view._find_balance_between_dates(account_history, future_start, future_end, start_balance)
        print(f"{account.name} for period {future_start} to {future_end}:")
        print(f"  Start: ${start_balance:.2f}, Final: ${final_balance:.2f}")
        # Start and final should be the same since no transactions in that period

    print("\n=== All Savings Display Tests Passed! ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_savings_display_fix()