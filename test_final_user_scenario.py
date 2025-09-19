"""
Final test with user's exact scenario and expected numbers
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_final_user_scenario():
    """Test user's exact scenario with expected numbers"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Final User Scenario Test ===")

    # User's exact setup
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=0.0,  # User wants auto-save = 0
        is_default_save=True,
        initial_balance=1000.0
    )

    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,  # User's bill sum
        initial_balance=100.0
    )

    print(f"Emergency fund start: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # User's paycheck
    today = date.today()
    paycheck_date = today - timedelta(days=1)
    paycheck_amount = 4625.0

    print(f"Paycheck: ${paycheck_amount}")

    # Process paycheck
    split = processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=paycheck_date,
        week_start_date=paycheck_date
    )

    print(f"Bill sum: ${split.bills_deducted}")
    print(f"Week1 start: ${split.week1_allocation}")
    print(f"Week2 start: ${split.week2_allocation}")

    # Week 1 spending
    week1_spending = 150.0
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": week1_spending,
        "date": paycheck_date + timedelta(days=1),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    print(f"Week1 spent: ${week1_spending}")
    print(f"Week1 current: ${split.week1_allocation - week1_spending}")

    # Check Week 2 after rollover
    weeks = tm.get_all_weeks()
    week2_transactions = tm.get_transactions_by_week(2)
    week2_rollover = sum(
        t.amount for t in week2_transactions
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    week2_total = split.week2_allocation + week2_rollover

    print(f"Week2 start: ${week2_total}")

    # Week 2 spending
    week2_spending = 200.0
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": week2_spending,
        "date": paycheck_date + timedelta(days=8),
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Week2 spent: ${week2_spending}")
    print(f"Week2 current: ${week2_total - week2_spending}")

    # Emergency fund before rollover
    print(f"Emergency fund start: ${1000.0}")

    # Process next paycheck to trigger rollover
    next_paycheck_date = today + timedelta(days=14)
    processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=next_paycheck_date,
        week_start_date=next_paycheck_date
    )

    final_balance = emergency_fund.get_current_balance(tm.db)
    emergency_change = final_balance - 1000.0

    print(f"Emergency fund final: ${final_balance}")
    print(f"Emergency fund change: ${emergency_change}")

    print(f"\n--- User's Expected Numbers ---")
    print(f"paycheck: 4625")
    print(f"Bill sum: 300")
    print(f"- Remaining: 4325")
    print(f"week1 start: 2162.50")
    print(f"week1 spent: 150")
    print(f"week1 current: 2012.50")
    print(f"- week1 Rollover: 2012.50")
    print(f"week2 start: 4175")
    print(f"week2 spent: 200")
    print(f"week2 current: 3975")
    print(f"- week2 Rollover: 3975")
    print(f"emergency fund start: 1000")
    print(f"emergency fund final: 4975")
    print(f"emergency found change: 3975")

    print(f"\n--- Actual Numbers ---")
    print(f"paycheck: {paycheck_amount}")
    print(f"Bill sum: {split.bills_deducted}")
    print(f"- Remaining: {paycheck_amount - split.bills_deducted}")
    print(f"week1 start: {split.week1_allocation}")
    print(f"week1 spent: {week1_spending}")
    print(f"week1 current: {split.week1_allocation - week1_spending}")
    print(f"- week1 Rollover: {split.week1_allocation - week1_spending}")
    print(f"week2 start: {week2_total}")
    print(f"week2 spent: {week2_spending}")
    print(f"week2 current: {week2_total - week2_spending}")
    print(f"- week2 Rollover: {week2_total - week2_spending}")
    print(f"emergency fund start: 1000")
    print(f"emergency fund final: {final_balance}")
    print(f"emergency found change: {emergency_change}")

    # Check matches
    print(f"\n--- Verification ---")
    expected_week1_start = 2162.50
    expected_week2_start = 4175.0
    expected_week2_rollover = 3975.0
    expected_emergency_final = 4975.0

    week1_match = abs(split.week1_allocation - expected_week1_start) < 0.01
    week2_match = abs(week2_total - expected_week2_start) < 0.01
    rollover_match = abs((week2_total - week2_spending) - expected_week2_rollover) < 0.01
    emergency_match = abs(final_balance - expected_emergency_final) < 0.01

    print(f"Week 1 allocation: {'✓' if week1_match else '✗'} (Expected: ${expected_week1_start}, Got: ${split.week1_allocation})")
    print(f"Week 2 total: {'✓' if week2_match else '✗'} (Expected: ${expected_week2_start}, Got: ${week2_total})")
    print(f"Week 2 rollover: {'✓' if rollover_match else '✗'} (Expected: ${expected_week2_rollover}, Got: ${week2_total - week2_spending})")
    print(f"Emergency final: {'✓' if emergency_match else '✗'} (Expected: ${expected_emergency_final}, Got: ${final_balance})")

    if week1_match and week2_match and rollover_match and emergency_match:
        print(f"\nSUCCESS: All numbers match user's expectations!")
    else:
        print(f"\nSome numbers still don't match. Need further investigation.")

    print("\n=== Final User Scenario Test Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_final_user_scenario()