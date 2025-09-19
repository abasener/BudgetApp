"""
Test if the Weekly View can properly display week data with the new system
"""

from datetime import date
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_weekly_view_display():
    """Test if weekly view can load and display data properly"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Testing Weekly View Data Display ===")

    # Create test data
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

    # Process paycheck to create weeks
    paycheck_split = processor.process_new_paycheck(
        paycheck_amount=2500.0,
        paycheck_date=date(2024, 1, 15),
        week_start_date=date(2024, 1, 15)
    )

    # Add some spending
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": 150.0,
        "date": date(2024, 1, 17),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": 200.0,
        "date": date(2024, 1, 25),
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print("\n--- Testing Week Data Retrieval (simulating WeeklyView) ---")

    # Test what WeeklyView.populate_week_list() would do
    weeks = tm.get_all_weeks()
    print(f"Total weeks found: {len(weeks)}")

    for week in weeks:
        print(f"\nWeek {week.week_number} ({week.start_date} to {week.end_date}):")
        print(f"  Running total: ${week.running_total:.2f}")

        # Test what WeekDetailWidget.load_week_data() would do
        transactions = tm.get_transactions_by_week(week.week_number)
        print(f"  Total transactions: {len(transactions)}")

        # Categorize transactions like the view does
        spending_txs = [t for t in transactions if t.is_spending and t.include_in_analytics]
        income_txs = [t for t in transactions if t.is_income]
        saving_txs = [t for t in transactions if t.is_saving]
        bill_pay_txs = [t for t in transactions if t.is_bill_pay]

        print(f"  Spending transactions: {len(spending_txs)}")
        print(f"  Income transactions: {len(income_txs)}")
        print(f"  Saving transactions: {len(saving_txs)}")
        print(f"  Bill pay transactions: {len(bill_pay_txs)}")

        # Calculate totals like the view does
        total_spending = sum(t.amount for t in spending_txs)
        total_income = sum(t.amount for t in income_txs)
        total_savings = sum(t.amount for t in saving_txs)

        print(f"  Total spending: ${total_spending:.2f}")
        print(f"  Total income: ${total_income:.2f}")
        print(f"  Total savings: ${total_savings:.2f}")

        # Calculate remaining money (what the progress bar would show)
        allocated_amount = week.running_total
        rollover_income = sum(t.amount for t in income_txs if "rollover" in t.description.lower() or t.category == "Rollover")
        effective_allocation = allocated_amount + rollover_income
        remaining = effective_allocation - total_spending

        print(f"  Allocated amount: ${allocated_amount:.2f}")
        print(f"  Rollover income: ${rollover_income:.2f}")
        print(f"  Effective allocation: ${effective_allocation:.2f}")
        print(f"  Remaining: ${remaining:.2f}")

        # Test category breakdown (for pie chart)
        category_totals = {}
        for tx in spending_txs:
            category = tx.category or "Other"
            category_totals[category] = category_totals.get(category, 0) + tx.amount

        if category_totals:
            print(f"  Category breakdown: {category_totals}")

    print("\n--- Testing Bi-weekly Period Grouping ---")

    # Test how WeeklyView groups weeks into bi-weekly periods
    weeks_dict = {week.week_number: week for week in weeks}
    max_week_num = max(week.week_number for week in weeks) if weeks else 0

    bi_weekly_periods = []
    current_week_num = max_week_num if max_week_num % 2 == 0 else max_week_num - 1

    while current_week_num >= 1:
        week1_num = current_week_num - 1  # Odd week
        week2_num = current_week_num      # Even week

        week1 = weeks_dict.get(week1_num)
        week2 = weeks_dict.get(week2_num)

        if week1 and week2:
            period = {
                'week1': week1,
                'week2': week2,
                'start_date': min(week1.start_date, week2.start_date),
                'end_date': max(week1.end_date, week2.end_date)
            }
            bi_weekly_periods.append(period)
            print(f"Bi-weekly period: Week {week1_num} & {week2_num} ({period['start_date']} to {period['end_date']})")

        current_week_num -= 2

    print(f"\nTotal bi-weekly periods created: {len(bi_weekly_periods)}")

    # Test what update_week_info would calculate
    if bi_weekly_periods:
        period = bi_weekly_periods[0]  # Most recent period
        print(f"\n--- Testing Period Info Calculation (Week {period['week1'].week_number} & {period['week2'].week_number}) ---")

        # Get all transactions for both weeks
        all_transactions = []
        for week_num in [period['week1'].week_number, period['week2'].week_number]:
            week_transactions = tm.get_transactions_by_week(week_num)
            all_transactions.extend(week_transactions)

        # Calculate paycheck amount (income transactions)
        income_transactions = [t for t in all_transactions if t.is_income]
        total_paycheck = sum(t.amount for t in income_transactions)
        print(f"Total paycheck for period: ${total_paycheck:.2f}")

        # Calculate savings payments
        savings_transactions = [t for t in all_transactions if t.is_saving]
        total_savings_payments = sum(t.amount for t in savings_transactions)
        print(f"Total savings for period: ${total_savings_payments:.2f}")

        # Calculate bill payments
        bill_transactions = [t for t in all_transactions if t.is_bill_pay]
        total_bill_payments = sum(t.amount for t in bill_transactions)
        print(f"Total bill payments for period: ${total_bill_payments:.2f}")

    print("\n=== Weekly View Display Test Complete ===")

    # Test account balance display
    print(f"\nFinal account balances:")
    print(f"Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"Rent Bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_weekly_view_display()