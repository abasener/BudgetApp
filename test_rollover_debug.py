"""
Debug test to isolate the rollover calculation issue
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_rollover_debug():
    """Debug the rollover calculation step by step"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Rollover Debug Test ===")

    # Step 1: Create accounts
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

    # Step 2: Process paycheck - should create Week 1 & 2 with $1525 each
    print("\n--- Step 2: Process Paycheck ---")
    paycheck_amount = 3350.0
    bill_savings = 300.0  # Rent bill saving
    account_savings = 200.0  # Emergency fund saving
    total_savings = bill_savings + account_savings
    weekly_allocation = (paycheck_amount - total_savings) / 2

    print(f"Paycheck: ${paycheck_amount}")
    print(f"Total savings: ${total_savings} (Bill: ${bill_savings}, Account: ${account_savings})")
    print(f"Expected weekly allocation: ${weekly_allocation}")

    # Use recent dates so rollover logic works correctly
    from datetime import timedelta
    today = date.today()
    paycheck_date = today - timedelta(days=3)  # A few days ago
    week_start_date = paycheck_date

    paycheck_split = processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=paycheck_date,
        week_start_date=week_start_date
    )

    print(f"Actual split: {paycheck_split}")

    # Check weeks after paycheck
    weeks = tm.get_all_weeks()
    print(f"\nWeeks after paycheck:")
    for week in weeks:
        print(f"  Week {week.week_number}: running_total=${week.running_total:.2f}")

    # Step 3: Add spending to Week 1
    print("\n--- Step 3: Add Spending to Week 1 ---")
    spending_amount = 150.0

    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": spending_amount,
        "date": paycheck_date + timedelta(days=2),  # 2 days after paycheck
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    print(f"Added ${spending_amount} spending to Week 1")

    # Step 4: Check what should rollover from Week 1
    print("\n--- Step 4: Calculate Expected Rollover ---")
    week1 = weeks[0]
    week1_transactions = tm.get_transactions_by_week(1)

    print(f"Week 1 transactions:")
    for tx in week1_transactions:
        print(f"  {tx}")

    # Calculate effective Week 1 allocation
    base_allocation = week1.running_total
    rollover_income = sum(
        t.amount for t in week1_transactions
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    total_allocation = base_allocation + rollover_income

    spending = sum(
        t.amount for t in week1_transactions
        if t.transaction_type in ["spending", "bill_pay"]
    )

    expected_rollover = total_allocation - spending

    print(f"Week 1 calculations:")
    print(f"  Base allocation: ${base_allocation:.2f}")
    print(f"  Rollover income: ${rollover_income:.2f}")
    print(f"  Total allocation: ${total_allocation:.2f}")
    print(f"  Spending: ${spending:.2f}")
    print(f"  Expected rollover to Week 2: ${expected_rollover:.2f}")

    # Step 5: Check Week 2 after rollover
    print("\n--- Step 5: Check Week 2 After Rollover ---")
    week2 = weeks[1]
    week2_transactions = tm.get_transactions_by_week(2)

    print(f"Week 2 transactions:")
    for tx in week2_transactions:
        print(f"  {tx}")

    # Calculate Week 2 effective allocation
    week2_base = week2.running_total
    week2_rollover_income = sum(
        t.amount for t in week2_transactions
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    week2_total_allocation = week2_base + week2_rollover_income

    print(f"Week 2 calculations:")
    print(f"  Base allocation (running_total): ${week2_base:.2f}")
    print(f"  Rollover income: ${week2_rollover_income:.2f}")
    print(f"  Total effective allocation: ${week2_total_allocation:.2f}")
    print(f"  Expected total allocation: ${week2_base + expected_rollover:.2f}")

    # Step 6: Add spending to Week 2
    print("\n--- Step 6: Add Spending to Week 2 ---")
    week2_spending = 200.0

    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": week2_spending,
        "date": paycheck_date + timedelta(days=10),  # 10 days after paycheck (in Week 2)
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Added ${week2_spending} spending to Week 2")

    # Step 7: Check final Week 2 calculations
    print("\n--- Step 7: Final Week 2 Calculations ---")
    week2_transactions_final = tm.get_transactions_by_week(2)

    week2_final_spending = sum(
        t.amount for t in week2_transactions_final
        if t.transaction_type in ["spending", "bill_pay"]
    )

    week2_final_rollover = week2_total_allocation - week2_final_spending

    print(f"Week 2 final calculations:")
    print(f"  Total allocation: ${week2_total_allocation:.2f}")
    print(f"  Total spending: ${week2_final_spending:.2f}")
    print(f"  Expected rollover to savings: ${week2_final_rollover:.2f}")

    # Step 8: Check emergency fund final balance
    print("\n--- Step 8: Check Emergency Fund Balance ---")
    current_balance = emergency_fund.get_current_balance(tm.db)
    expected_balance = 1000.0 + 200.0 + week2_final_rollover  # initial + auto_save + rollover

    print(f"Emergency fund balance: ${current_balance:.2f}")
    print(f"Expected balance: ${expected_balance:.2f}")
    print(f"Difference: ${current_balance - expected_balance:.2f}")

    # Step 9: Check emergency fund history
    print("\n--- Step 9: Emergency Fund History ---")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    print("\n=== Rollover Debug Test Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_rollover_debug()