"""
Test the complete backend flow with clean data to verify everything works
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction
from datetime import date, timedelta

def test_backend_flow():
    """Test complete paycheck processing and rollover flow"""

    print("=== BACKEND FLOW TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Verify clean state
        print("\n1. VERIFYING CLEAN STATE:")
        transactions = db.query(Transaction).count()
        weeks = db.query(Week).count()
        bills = transaction_manager.get_all_bills()
        accounts = transaction_manager.get_all_accounts()

        print(f"  Transactions: {transactions}")
        print(f"  Weeks: {weeks}")
        print(f"  Bills: {len(bills)}")
        for bill in bills:
            print(f"    {bill.name}: amount_to_save={bill.amount_to_save}, balance=${bill.running_total:.2f}")
        print(f"  Savings accounts: {len(accounts)}")
        for account in accounts:
            print(f"    {account.name}: balance=${account.running_total:.2f}, default={account.is_default_save}")

        # STEP 2: Process a test paycheck
        print("\n2. PROCESSING TEST PAYCHECK:")
        test_amount = 1500.0
        test_date = date.today()
        week_start = date.today() - timedelta(days=date.today().weekday())  # Start of current week

        print(f"  Paycheck: ${test_amount:.2f}")
        print(f"  Date: {test_date}")
        print(f"  Week start: {week_start}")

        # Calculate expected deductions
        expected_bills = sum(
            bill.amount_to_save * test_amount if bill.amount_to_save < 1.0
            else bill.amount_to_save
            for bill in bills
        )
        expected_remaining = test_amount - expected_bills
        expected_per_week = expected_remaining / 2

        print(f"  Expected bill deductions: ${expected_bills:.2f}")
        print(f"  Expected remaining: ${expected_remaining:.2f}")
        print(f"  Expected per week: ${expected_per_week:.2f}")

        # Process the paycheck
        split = paycheck_processor.process_new_paycheck(test_amount, test_date, week_start)

        print(f"  Actual split results:")
        print(f"    Bills deducted: ${split.bills_deducted:.2f}")
        print(f"    Remaining for weeks: ${split.remaining_for_weeks:.2f}")
        print(f"    Week 1 allocation: ${split.week1_allocation:.2f}")
        print(f"    Week 2 allocation: ${split.week2_allocation:.2f}")

        # STEP 3: Check created weeks and transactions
        print("\n3. CHECKING CREATED DATA:")
        new_weeks = db.query(Week).order_by(Week.week_number).all()
        new_transactions = db.query(Transaction).order_by(Transaction.week_number, Transaction.id).all()

        print(f"  Weeks created: {len(new_weeks)}")
        for week in new_weeks:
            print(f"    Week {week.week_number}: ${week.running_total:.2f} ({week.start_date} to {week.end_date})")

        print(f"  Transactions created: {len(new_transactions)}")
        for tx in new_transactions:
            account_info = ""
            if hasattr(tx, 'account_saved_to') and tx.account_saved_to:
                account_info = f" -> {tx.account_saved_to}"
            elif hasattr(tx, 'bill_id') and tx.bill_id:
                account_info = f" -> bill_id {tx.bill_id}"
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}{account_info}")

        # STEP 4: Test rollover calculations
        print("\n4. TESTING ROLLOVER CALCULATIONS:")
        if len(new_weeks) >= 2:
            week1 = new_weeks[0]
            week2 = new_weeks[1]

            # Calculate Week 1 rollover
            rollover1 = paycheck_processor.calculate_week_rollover(week1.week_number)
            print(f"  Week {week1.week_number} rollover:")
            print(f"    Allocated: ${rollover1.allocated_amount:.2f}")
            print(f"    Spent: ${rollover1.spent_amount:.2f}")
            print(f"    Rollover: ${rollover1.rollover_amount:.2f}")

            # Calculate Week 2 effective balance (before rollover processing)
            week2_tx = [tx for tx in new_transactions if tx.week_number == week2.week_number]
            week2_rollover_income = sum(tx.amount for tx in week2_tx if tx.transaction_type == "income" and "rollover" in tx.description.lower())
            week2_rollover_deficit = sum(tx.amount for tx in week2_tx if tx.transaction_type == "spending" and "rollover" in tx.description.lower())
            week2_starting = week2.running_total + week2_rollover_income - week2_rollover_deficit

            print(f"  Week {week2.week_number} before rollover processing:")
            print(f"    Base allocation: ${week2.running_total:.2f}")
            print(f"    Rollover income: ${week2_rollover_income:.2f}")
            print(f"    Rollover deficit: ${week2_rollover_deficit:.2f}")
            print(f"    Starting amount: ${week2_starting:.2f}")

        # STEP 5: Check bill and account updates
        print("\n5. CHECKING BILL AND ACCOUNT UPDATES:")
        updated_bills = transaction_manager.get_all_bills()
        for bill in updated_bills:
            print(f"  {bill.name}: balance=${bill.running_total:.2f}")

        updated_accounts = transaction_manager.get_all_accounts()
        for account in updated_accounts:
            print(f"  {account.name}: balance=${account.running_total:.2f}")

        # STEP 6: Expected vs Actual verification
        print("\n6. VERIFICATION:")
        week1_allocation_correct = abs(split.week1_allocation - expected_per_week) < 0.01
        week2_allocation_correct = abs(split.week2_allocation - expected_per_week) < 0.01
        bills_deducted_correct = abs(split.bills_deducted - expected_bills) < 0.01

        print(f"  Week 1 allocation correct: {week1_allocation_correct} (${split.week1_allocation:.2f} vs ${expected_per_week:.2f})")
        print(f"  Week 2 allocation correct: {week2_allocation_correct} (${split.week2_allocation:.2f} vs ${expected_per_week:.2f})")
        print(f"  Bills deducted correct: {bills_deducted_correct} (${split.bills_deducted:.2f} vs ${expected_bills:.2f})")

        all_correct = week1_allocation_correct and week2_allocation_correct and bills_deducted_correct
        print(f"  All calculations correct: {all_correct}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_backend_flow()