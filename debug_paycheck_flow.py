"""
Debug the complete paycheck processing flow to see where bills are handled
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction

def debug_paycheck_flow():
    """Debug the complete paycheck flow from start to finish"""

    print("=== PAYCHECK PROCESSING FLOW DEBUG ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Show current state before any processing
        print("\n1. CURRENT STATE:")
        all_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in all_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}")

        # Show all current transactions
        print("\n2. CURRENT TRANSACTIONS:")
        all_transactions = db.query(Transaction).order_by(Transaction.week_number, Transaction.id).all()
        for tx in all_transactions:
            account_info = ""
            if hasattr(tx, 'account_saved_to') and tx.account_saved_to:
                account_info = f" -> {tx.account_saved_to}"
            elif hasattr(tx, 'account_id') and tx.account_id:
                account_info = f" (account_id: {tx.account_id})"

            print(f"  Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}{account_info}")

        # STEP 3: Show how Week 1 gets its current value
        print("\n3. WEEK 1 CALCULATION BREAKDOWN:")
        week1 = next((w for w in all_weeks if w.week_number == 1), None)
        if week1:
            print(f"  Week 1 stored running_total: ${week1.running_total:.2f}")

            week1_transactions = [tx for tx in all_transactions if tx.week_number == 1]
            print(f"  Week 1 transactions ({len(week1_transactions)}):")

            total_income = 0
            total_spending = 0
            total_bills = 0
            total_saving = 0

            for tx in week1_transactions:
                print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")
                if tx.transaction_type == "income":
                    total_income += tx.amount
                elif tx.transaction_type == "spending":
                    total_spending += tx.amount
                elif tx.transaction_type == "bill_pay":
                    total_bills += tx.amount
                elif tx.transaction_type == "saving":
                    total_saving += tx.amount

            print(f"  Week 1 transaction totals:")
            print(f"    Income: +${total_income:.2f}")
            print(f"    Spending: -${total_spending:.2f}")
            print(f"    Bills: -${total_bills:.2f}")
            print(f"    Saving: -${total_saving:.2f}")

            calculated_balance = week1.running_total + total_income - total_spending - total_bills - total_saving
            print(f"  Week 1 calculated effective balance: ${calculated_balance:.2f}")

        # STEP 4: Show original paycheck details
        print("\n4. PAYCHECK ANALYSIS:")
        paycheck_transactions = [tx for tx in all_transactions if "paycheck" in tx.description.lower()]
        for tx in paycheck_transactions:
            print(f"  {tx.description}: ${tx.amount:.2f}")

        # Check if there are any bill allocation transactions
        bill_allocations = [tx for tx in all_transactions if "allocation" in tx.description.lower()]
        print(f"  Bill/Saving allocations: {len(bill_allocations)}")
        for tx in bill_allocations:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

        # STEP 5: Expected vs Actual
        print("\n5. EXPECTED BEHAVIOR:")
        print("  For $1500 paycheck:")
        print("    1. Deduct bills/savings from $1500")
        print("    2. Split remaining amount between Week 1 and Week 2")
        print("    3. Week 1 should start with half of remaining")
        print("    4. Week 2 should start with half of remaining")
        print("    5. If no spending, Week 1 rollover = Week 1 starting amount")
        print("    6. Week 2 effective = Week 2 starting + Week 1 rollover")

        # Calculate what it should be
        total_bills_savings = sum(tx.amount for tx in all_transactions if tx.transaction_type in ["saving"] and "allocation" in tx.description.lower())
        print(f"  Total bill/saving allocations: ${total_bills_savings:.2f}")
        remaining_after_bills = 1500 - total_bills_savings
        week_allocation = remaining_after_bills / 2
        print(f"  Remaining after bills: ${remaining_after_bills:.2f}")
        print(f"  Each week should get: ${week_allocation:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    debug_paycheck_flow()