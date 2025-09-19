"""
Debug the fundamental paycheck splitting and rollover logic
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def debug_paycheck_logic():
    """Debug step by step what's happening vs what should happen"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Debugging Paycheck Logic ===")

    # Create Emergency Fund account
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=300.0,  # User's amount from the data
        is_default_save=True,
        initial_balance=1000.0
    )

    # Create Bill - only one for simplicity
    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,  # User's bill sum
        initial_balance=100.0
    )

    print(f"Initial Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"Initial Rent Bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    # User's paycheck amount
    paycheck_amount = 4625.0

    # Step 1: Check what the paycheck processor calculates
    print(f"\n=== Step 1: Paycheck Calculation Logic ===")
    print(f"Gross paycheck: ${paycheck_amount}")

    # Let's see what the processor calculates for bills and splits
    bills_deduction = processor.calculate_bills_deduction(paycheck_amount)
    account_auto_savings = processor.calculate_account_auto_savings()
    remaining_for_weeks = paycheck_amount - bills_deduction - account_auto_savings
    week1_allocation = remaining_for_weeks / 2
    week2_allocation = remaining_for_weeks / 2

    print(f"Bills deduction calculated: ${bills_deduction}")
    print(f"Account auto-savings calculated: ${account_auto_savings}")
    print(f"Remaining for weeks: ${remaining_for_weeks}")
    print(f"Week 1 allocation: ${week1_allocation}")
    print(f"Week 2 allocation: ${week2_allocation}")

    print(f"\nUser expected:")
    print(f"Bills: $300")
    print(f"Account savings: (not specified, assuming $300)")
    print(f"Remaining: $4325")
    print(f"Per week: $2162.50")

    # Step 2: Process the actual paycheck
    print(f"\n=== Step 2: Process Paycheck ===")
    today = date.today()
    paycheck_date = today - timedelta(days=1)

    split = processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=paycheck_date,
        week_start_date=paycheck_date
    )

    print(f"Actual split result: {split}")

    # Check balances after paycheck
    print(f"\nBalances after paycheck:")
    print(f"Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"Rent Bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Step 3: Check week allocations
    print(f"\n=== Step 3: Week Allocations ===")
    weeks = tm.get_all_weeks()
    for week in weeks:
        transactions = tm.get_transactions_by_week(week.week_number)
        print(f"\nWeek {week.week_number}:")
        print(f"  running_total (base allocation): ${week.running_total:.2f}")

        # Calculate effective allocation
        rollover_income = sum(
            t.amount for t in transactions
            if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
        )
        effective_allocation = week.running_total + rollover_income
        print(f"  rollover income: ${rollover_income:.2f}")
        print(f"  effective allocation: ${effective_allocation:.2f}")

        # Show all transactions
        print(f"  transactions:")
        for tx in transactions:
            print(f"    {tx}")

    # Step 4: Add Week 1 spending
    print(f"\n=== Step 4: Week 1 Spending ===")
    week1_spending = 150.0

    print(f"Emergency Fund before Week 1 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": week1_spending,
        "date": paycheck_date + timedelta(days=1),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    print(f"Added Week 1 spending: ${week1_spending}")
    print(f"Emergency Fund after Week 1 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check Week 2 after rollover
    print(f"\nWeek 2 after Week 1 rollover:")
    week2_transactions = tm.get_transactions_by_week(2)
    week2_rollover = sum(
        t.amount for t in week2_transactions
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    week2_effective = weeks[1].running_total + week2_rollover
    print(f"  Week 2 base: ${weeks[1].running_total:.2f}")
    print(f"  Week 2 rollover income: ${week2_rollover:.2f}")
    print(f"  Week 2 effective allocation: ${week2_effective:.2f}")

    expected_week1_remaining = week1_allocation - week1_spending
    print(f"  Expected Week 1 remaining: ${expected_week1_remaining:.2f}")
    print(f"  Expected Week 2 total: ${week2_allocation + expected_week1_remaining:.2f}")

    # Step 5: Add Week 2 spending
    print(f"\n=== Step 5: Week 2 Spending ===")
    week2_spending = 200.0

    print(f"Emergency Fund before Week 2 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": week2_spending,
        "date": paycheck_date + timedelta(days=8),
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Added Week 2 spending: ${week2_spending}")
    print(f"Emergency Fund after Week 2 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    week2_remaining = week2_effective - week2_spending
    print(f"Week 2 remaining (should go to savings): ${week2_remaining:.2f}")

    # Step 6: Process next paycheck to trigger Week 2 rollover
    print(f"\n=== Step 6: Next Paycheck (triggers Week 2 rollover) ===")
    print(f"Emergency Fund before next paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    next_paycheck_date = today + timedelta(days=14)
    split2 = processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=next_paycheck_date,
        week_start_date=next_paycheck_date
    )

    print(f"Emergency Fund after next paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Step 7: Final analysis
    print(f"\n=== Step 7: Final Analysis ===")

    expected_emergency_final = (
        1000.0 +  # Starting
        300.0 +   # First paycheck auto-save
        300.0 +   # Second paycheck auto-save
        week2_remaining  # Week 2 rollover
    )

    actual_emergency_final = emergency_fund.get_current_balance(tm.db)

    print(f"Expected Emergency Fund final: ${expected_emergency_final:.2f}")
    print(f"  Starting: $1000.00")
    print(f"  Auto-save 1: $300.00")
    print(f"  Auto-save 2: $300.00")
    print(f"  Week 2 rollover: ${week2_remaining:.2f}")

    print(f"Actual Emergency Fund final: ${actual_emergency_final:.2f}")
    print(f"Difference: ${actual_emergency_final - expected_emergency_final:.2f}")

    # Show complete Emergency Fund history
    print(f"\n=== Emergency Fund Complete History ===")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    # Check for discrepancies
    print(f"\n=== Discrepancy Analysis ===")

    if abs(week1_allocation - 2162.50) > 0.01:
        print(f"❌ Week allocation wrong: got ${week1_allocation:.2f}, expected $2162.50")
        print(f"   Issue likely in paycheck splitting logic")

    if abs(week2_effective - 4175.0) > 0.01:
        print(f"❌ Week 2 effective allocation wrong: got ${week2_effective:.2f}, expected $4175.00")
        print(f"   Issue likely in rollover calculation or duplicate transactions")

    if abs(actual_emergency_final - 4975.0) > 0.01:
        print(f"❌ Emergency fund final wrong: got ${actual_emergency_final:.2f}, expected $4975.00")
        print(f"   Issue likely in rollover-to-savings or duplicate auto-saves")

    print("\n=== Debug Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    debug_paycheck_logic()