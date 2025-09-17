"""
Debug why Weeks 1 and 2 aren't being processed
"""

from datetime import date
from services.transaction_manager import TransactionManager
from models import get_db, Week

def debug_completion_criteria():
    """Debug week completion criteria"""

    print("Debug Week Completion Criteria")
    print("=" * 40)

    transaction_manager = TransactionManager()

    try:
        db = get_db()

        # Get all weeks that should be processed
        weeks_pending = db.query(Week).filter(Week.rollover_applied == False).order_by(Week.week_number).all()

        print(f"Weeks with rollover_applied = False: {len(weeks_pending)}")

        for week in weeks_pending:
            print(f"\n--- Week {week.week_number} ---")
            print(f"  start_date: {week.start_date}")
            print(f"  end_date: {week.end_date}")
            print(f"  running_total: ${week.running_total:.2f}")

            # Check completion criteria
            next_week = db.query(Week).filter(Week.week_number == week.week_number + 1).first()
            week_ended = date.today() > week.end_date
            is_week1_of_period = (week.week_number % 2) == 1

            print(f"  Completion check:")
            print(f"    Has next week: {next_week is not None}")
            if next_week:
                print(f"      Next week: {next_week.week_number}")
            print(f"    Week ended: {week_ended} (today: {date.today()})")
            print(f"    Is Week 1: {is_week1_of_period}")

            # Determine processing decision
            should_process = next_week or week_ended
            print(f"    Should process: {should_process}")

            if should_process:
                if is_week1_of_period and next_week:
                    print(f"    -> Should rollover Week {week.week_number} to Week {next_week.week_number}")
                elif not is_week1_of_period:
                    print(f"    -> Should rollover Week {week.week_number} to savings")
                else:
                    print(f"    -> Week 1 without next week, should wait")
            else:
                print(f"    -> Not ready for processing")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    debug_completion_criteria()