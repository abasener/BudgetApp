"""
Debug why Week 4 isn't being processed for rollover
"""

from datetime import date
from services.transaction_manager import TransactionManager
from models import get_db, Week

def debug_week4_completion():
    """Debug Week 4 completion logic"""

    print("Debugging Week 4 Completion Logic")
    print("=" * 40)

    transaction_manager = TransactionManager()

    try:
        db = get_db()

        # Get Week 4
        week4 = db.query(Week).filter(Week.week_number == 4).first()
        if not week4:
            print("Week 4 not found")
            return

        print(f"Week 4 details:")
        print(f"  week_number: {week4.week_number}")
        print(f"  start_date: {week4.start_date}")
        print(f"  end_date: {week4.end_date}")
        print(f"  running_total: ${week4.running_total:.2f}")
        print(f"  rollover_applied: {week4.rollover_applied}")

        # Check completion criteria
        next_week = db.query(Week).filter(Week.week_number == week4.week_number + 1).first()
        week_ended = date.today() > week4.end_date
        is_week1_of_period = (week4.week_number % 2) == 1

        print(f"\nCompletion check:")
        print(f"  Has next week (Week 5): {next_week is not None}")
        print(f"  Week ended (today > {week4.end_date}): {week_ended}")
        print(f"  Today's date: {date.today()}")
        print(f"  Is Week 1 of period (odd number): {is_week1_of_period}")
        print(f"  Should process: {next_week or week_ended}")

        if next_week or week_ended:
            if is_week1_of_period and next_week:
                print(f"  -> Should rollover to Week 5")
            elif not is_week1_of_period:
                print(f"  -> Should rollover to savings (Week 2 of period)")
            else:
                print(f"  -> Week 1 with no next week, should wait")
        else:
            print(f"  -> Week not complete yet, should not process")

        # Check why it's not being processed
        weeks_pending = db.query(Week).filter(Week.rollover_applied == False).all()
        print(f"\nWeeks with rollover_applied = False: {len(weeks_pending)}")
        for week in weeks_pending:
            print(f"  Week {week.week_number}: {week.start_date} to {week.end_date}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    debug_week4_completion()