"""
Test the Week Tab Flow and Rollover Logic
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_week_tab_flow():
    """Test the complete week tab flow step by step"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Week Tab Flow Analysis ===")

    # Step 1: Set up basic accounts and bills
    print("\n--- Step 1: Initial Setup ---")

    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=200.0,
        is_default_save=True,
        initial_balance=1000.0
    )

    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,
        initial_balance=100.0
    )

    print(f"Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"Rent Bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Step 2: Process first paycheck - this should create Week 1 and Week 2
    print("\n--- Step 2: First Paycheck (creates Week 1 & 2) ---")

    paycheck1_split = processor.process_new_paycheck(
        paycheck_amount=2500.0,
        paycheck_date=date(2024, 1, 15),
        week_start_date=date(2024, 1, 15)
    )

    # Check what weeks exist now
    weeks = tm.get_all_weeks()
    print(f"\nWeeks after first paycheck: {len(weeks)}")
    for week in weeks:
        print(f"  Week {week.week_number}: ${week.running_total:.2f} ({week.start_date} to {week.end_date}) - Rollover Applied: {week.rollover_applied}")

    # Step 3: Add some spending to Week 1
    print("\n--- Step 3: Add Spending to Week 1 ---")

    spending1 = tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": 150.0,
        "date": date(2024, 1, 17),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    spending2 = tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": 75.0,
        "date": date(2024, 1, 19),
        "description": "Gas",
        "category": "Transportation",
        "include_in_analytics": True
    })

    print(f"Added spending: {spending1}")
    print(f"Added spending: {spending2}")

    # Check weeks after spending
    weeks = tm.get_all_weeks()
    print(f"\nWeeks after spending:")
    for week in weeks:
        print(f"  Week {week.week_number}: ${week.running_total:.2f} - Rollover Applied: {week.rollover_applied}")

    # Step 4: Add some spending to Week 2
    print("\n--- Step 4: Add Spending to Week 2 ---")

    spending3 = tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": 200.0,
        "date": date(2024, 1, 25),
        "description": "Dining out",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Added spending: {spending3}")

    # Check weeks after Week 2 spending
    weeks = tm.get_all_weeks()
    print(f"\nWeeks after Week 2 spending:")
    for week in weeks:
        print(f"  Week {week.week_number}: ${week.running_total:.2f} - Rollover Applied: {week.rollover_applied}")

    # Step 5: Process second paycheck - this should create Week 3 & 4 and trigger rollovers
    print("\n--- Step 5: Second Paycheck (creates Week 3 & 4, triggers rollovers) ---")

    paycheck2_split = processor.process_new_paycheck(
        paycheck_amount=2500.0,
        paycheck_date=date(2024, 1, 29),
        week_start_date=date(2024, 1, 29)
    )

    # Check all weeks and their rollover status
    weeks = tm.get_all_weeks()
    print(f"\nWeeks after second paycheck: {len(weeks)}")
    for week in weeks:
        print(f"  Week {week.week_number}: ${week.running_total:.2f} ({week.start_date} to {week.end_date}) - Rollover Applied: {week.rollover_applied}")

    # Step 6: Check account balances to see rollover effects
    print("\n--- Step 6: Account Balances After Rollovers ---")

    print(f"Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"Rent Bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Step 7: Check transactions to see rollover entries
    print("\n--- Step 7: Rollover Transactions ---")

    all_transactions = []
    for week in weeks:
        week_txs = tm.get_transactions_by_week(week.week_number)
        all_transactions.extend(week_txs)

    rollover_transactions = [tx for tx in all_transactions if "rollover" in tx.description.lower() or tx.category == "Rollover"]

    print(f"Found {len(rollover_transactions)} rollover transactions:")
    for tx in rollover_transactions:
        print(f"  {tx}")

    # Step 8: Manual rollover check to understand the logic
    print("\n--- Step 8: Manual Rollover Calculations ---")

    for week in weeks:
        if week.week_number <= 2:  # Only check first two weeks
            week_transactions = tm.get_transactions_by_week(week.week_number)

            # Calculate what we expect
            base_allocation = week.running_total

            # Get rollover income for this week
            rollover_income = sum(
                t.amount for t in week_transactions
                if t.transaction_type == "income" and
                ("rollover" in t.description.lower() or t.category == "Rollover")
            )

            # Calculate spending
            spending = sum(
                t.amount for t in week_transactions
                if t.transaction_type in ["spending", "bill_pay"]
            )

            allocated_amount = base_allocation + rollover_income
            remaining = allocated_amount - spending

            print(f"Week {week.week_number}:")
            print(f"  Base allocation: ${base_allocation:.2f}")
            print(f"  Rollover income: ${rollover_income:.2f}")
            print(f"  Total allocated: ${allocated_amount:.2f}")
            print(f"  Spending: ${spending:.2f}")
            print(f"  Remaining (rollover): ${remaining:.2f}")

    print("\n=== Week Tab Flow Analysis Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_week_tab_flow()