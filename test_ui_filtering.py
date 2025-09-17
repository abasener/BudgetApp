"""
Test the UI filtering logic to ensure rollover/allocation transactions are properly excluded
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction
from datetime import date

def test_ui_filtering():
    """Test that UI properly filters out rollover and allocation transactions"""

    print("=== UI FILTERING TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Get current state with rollover transactions
        print("\n1. CURRENT TRANSACTION STATE:")
        all_transactions = db.query(Transaction).order_by(Transaction.week_number, Transaction.id).all()

        week1_transactions = [tx for tx in all_transactions if tx.week_number == 1]
        week2_transactions = [tx for tx in all_transactions if tx.week_number == 2]

        print(f"  Week 1 transactions ({len(week1_transactions)}):")
        for tx in week1_transactions:
            print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description} (category: {tx.category})")

        print(f"  Week 2 transactions ({len(week2_transactions)}):")
        for tx in week2_transactions:
            print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description} (category: {tx.category})")

        # STEP 2: Test UI filtering logic for Week 1
        print("\n2. WEEK 1 UI FILTERING:")

        # Apply the same filtering logic as weekly_view.py
        week1_spending_for_ui = [
            t for t in week1_transactions
            if t.is_spending and t.include_in_analytics
            and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
            and not (t.description and "allocation" in t.description.lower())
        ]

        print(f"  All Week 1 transactions: {len(week1_transactions)}")
        print(f"  Week 1 spending transactions (after filtering): {len(week1_spending_for_ui)}")
        print(f"  Week 1 spending transactions for UI:")
        for tx in week1_spending_for_ui:
            print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

        week1_total_spending = sum(tx.amount for tx in week1_spending_for_ui)
        print(f"  Week 1 total spending for UI: ${week1_total_spending:.2f}")

        # STEP 3: Test UI filtering logic for Week 2
        print("\n3. WEEK 2 UI FILTERING:")

        week2_spending_for_ui = [
            t for t in week2_transactions
            if t.is_spending and t.include_in_analytics
            and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
            and not (t.description and "allocation" in t.description.lower())
        ]

        print(f"  All Week 2 transactions: {len(week2_transactions)}")
        print(f"  Week 2 spending transactions (after filtering): {len(week2_spending_for_ui)}")
        print(f"  Week 2 spending transactions for UI:")
        for tx in week2_spending_for_ui:
            print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

        week2_total_spending = sum(tx.amount for tx in week2_spending_for_ui)
        print(f"  Week 2 total spending for UI: ${week2_total_spending:.2f}")

        # STEP 4: Test what should be excluded
        print("\n4. EXCLUDED TRANSACTIONS:")

        excluded_transactions = [
            t for t in all_transactions
            if (t.category == "Rollover"
                or (t.description and "rollover" in t.description.lower())
                or (t.description and "allocation" in t.description.lower())
                or t.transaction_type == "saving"
                or t.transaction_type == "income")
        ]

        print(f"  Excluded transactions: {len(excluded_transactions)}")
        for tx in excluded_transactions:
            reason = ""
            if tx.category == "Rollover":
                reason = "Rollover category"
            elif tx.description and "rollover" in tx.description.lower():
                reason = "Rollover in description"
            elif tx.description and "allocation" in tx.description.lower():
                reason = "Allocation in description"
            elif tx.transaction_type == "saving":
                reason = "Saving transaction"
            elif tx.transaction_type == "income":
                reason = "Income transaction"

            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description} ({reason})")

        # STEP 5: Add a real spending transaction to test
        print("\n5. ADDING TEST SPENDING TRANSACTION:")
        test_spending = {
            "transaction_type": "spending",
            "week_number": 1,
            "amount": 25.50,
            "date": date.today(),
            "description": "Coffee shop purchase",
            "category": "Food"
        }

        transaction_manager.add_transaction(test_spending)
        print(f"  Added: ${test_spending['amount']:.2f} - {test_spending['description']}")

        # Re-test filtering after adding real spending
        updated_week1_transactions = db.query(Transaction).filter(Transaction.week_number == 1).all()
        updated_week1_spending_for_ui = [
            t for t in updated_week1_transactions
            if t.is_spending and t.include_in_analytics
            and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
            and not (t.description and "allocation" in t.description.lower())
        ]

        print(f"  Week 1 spending after test transaction: {len(updated_week1_spending_for_ui)}")
        for tx in updated_week1_spending_for_ui:
            print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

        updated_week1_total_spending = sum(tx.amount for tx in updated_week1_spending_for_ui)
        print(f"  Week 1 total spending (with test): ${updated_week1_total_spending:.2f}")

        # STEP 6: Verification
        print("\n6. VERIFICATION:")
        print(f"  Expected results:")
        print(f"    Week 1 should only show actual spending transactions (not rollovers/allocations)")
        print(f"    Week 2 should only show actual spending transactions (not rollovers)")
        print(f"    Total spending should exclude all rollover/allocation amounts")

        week1_correct = updated_week1_total_spending == 25.50  # Only the test transaction
        week2_correct = week2_total_spending == 0.00  # No actual spending

        print(f"  Week 1 filtering correct: {week1_correct} (${updated_week1_total_spending:.2f} should be $25.50)")
        print(f"  Week 2 filtering correct: {week2_correct} (${week2_total_spending:.2f} should be $0.00)")

        all_correct = week1_correct and week2_correct
        print(f"  All filtering correct: {all_correct}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_ui_filtering()