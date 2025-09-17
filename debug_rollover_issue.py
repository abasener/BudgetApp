"""
Debug the rollover logic and display issues
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor

def debug_rollover_issue():
    """Debug current rollover state and logic"""

    print("Debugging Rollover Logic and Display")
    print("=" * 50)

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        # Check current state
        all_weeks = transaction_manager.get_all_weeks()
        all_transactions = transaction_manager.get_all_transactions()
        default_savings = transaction_manager.get_default_savings_account()

        print(f"Current state:")
        print(f"  Weeks: {len(all_weeks)}")
        print(f"  Transactions: {len(all_transactions)}")
        print(f"  Default savings balance: ${default_savings.running_total:.2f}")

        if not all_weeks:
            print("No weeks found - need to add paycheck first")
            return

        # Sort weeks and analyze
        weeks_sorted = sorted(all_weeks, key=lambda w: w.week_number)

        print(f"\nWeek analysis:")
        for week in weeks_sorted:
            print(f"\n  Week {week.week_number}:")
            print(f"    running_total: ${week.running_total:.2f}")
            print(f"    rollover_applied: {week.rollover_applied}")
            print(f"    dates: {week.start_date} to {week.end_date}")

            # Get transactions for this week
            week_transactions = [t for t in all_transactions if t.week_number == week.week_number]
            print(f"    transactions: {len(week_transactions)}")

            for tx in week_transactions:
                print(f"      {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

            # Calculate what rollover should be
            try:
                rollover = paycheck_processor.calculate_week_rollover(week.week_number)
                print(f"    calculated rollover: ${rollover.rollover_amount:.2f}")
                print(f"      allocated: ${rollover.allocated_amount:.2f}")
                print(f"      spent: ${rollover.spent_amount:.2f}")
                print(f"      remaining: ${rollover.remaining_amount:.2f}")
            except Exception as e:
                print(f"    rollover calculation error: {e}")

        # Check rollover logic flow
        print(f"\nRollover logic check:")

        # Check if Week 1 should rollover to Week 2
        week1 = next((w for w in weeks_sorted if w.week_number % 2 == 1), None)
        week2 = next((w for w in weeks_sorted if w.week_number % 2 == 0), None)

        if week1 and week2:
            print(f"  Week 1 ({week1.week_number}): ${week1.running_total:.2f}, rollover_applied: {week1.rollover_applied}")
            print(f"  Week 2 ({week2.week_number}): ${week2.running_total:.2f}, rollover_applied: {week2.rollover_applied}")

            # Manual rollover calculation for Week 1
            week1_transactions = [t for t in all_transactions if t.week_number == week1.week_number]
            week1_spent = sum(t.amount for t in week1_transactions if t.transaction_type in ['spending', 'bill_pay'])
            week1_surplus = week1.running_total - week1_spent

            print(f"  Week 1 manual calculation:")
            print(f"    allocated: ${week1.running_total:.2f}")
            print(f"    spent: ${week1_spent:.2f}")
            print(f"    surplus/deficit: ${week1_surplus:.2f}")

            if week1_surplus != 0:
                expected_week2 = week2.running_total
                if not week1.rollover_applied:
                    expected_week2 = week1_surplus  # This would be added if rollover processed
                    print(f"  Expected Week 2 after rollover: original + rollover = ${expected_week2:.2f}")
                else:
                    print(f"  Week 1 rollover already applied")

        # Check if Week 2 should rollover to savings
        if week2:
            week2_transactions = [t for t in all_transactions if t.week_number == week2.week_number]
            week2_spent = sum(t.amount for t in week2_transactions if t.transaction_type in ['spending', 'bill_pay'])
            week2_surplus = week2.running_total - week2_spent

            print(f"  Week 2 manual calculation:")
            print(f"    allocated: ${week2.running_total:.2f}")
            print(f"    spent: ${week2_spent:.2f}")
            print(f"    surplus/deficit: ${week2_surplus:.2f}")

            if week2_surplus != 0:
                expected_savings = default_savings.running_total
                if not week2.rollover_applied:
                    expected_savings += week2_surplus
                    print(f"  Expected savings after rollover: ${expected_savings:.2f}")
                else:
                    print(f"  Week 2 rollover already applied")

        # Test rollover processing
        print(f"\nTesting rollover processing...")
        paycheck_processor.check_and_process_rollovers()

        # Check state after rollover processing
        print(f"\nAfter rollover processing:")
        updated_weeks = transaction_manager.get_all_weeks()
        updated_savings = transaction_manager.get_default_savings_account()

        weeks_sorted_after = sorted(updated_weeks, key=lambda w: w.week_number)
        for week in weeks_sorted_after:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        print(f"  Savings balance: ${updated_savings.running_total:.2f}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    debug_rollover_issue()