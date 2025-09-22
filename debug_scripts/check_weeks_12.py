"""
Check what happened to Weeks 1 and 2
"""

from services.transaction_manager import TransactionManager
from models import get_db, Week

def check_weeks_12():
    """Check status of Weeks 1 and 2"""

    print("Checking Weeks 1 and 2 Status")
    print("=" * 35)

    transaction_manager = TransactionManager()

    try:
        db = get_db()

        # Get all weeks
        all_weeks = db.query(Week).order_by(Week.week_number).all()

        print(f"All weeks in database:")
        for week in all_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        # Specifically check Weeks 1 and 2
        week1 = db.query(Week).filter(Week.week_number == 1).first()
        week2 = db.query(Week).filter(Week.week_number == 2).first()

        if week1:
            print(f"\nWeek 1 details:")
            print(f"  rollover_applied: {week1.rollover_applied}")
            print(f"  dates: {week1.start_date} to {week1.end_date}")
        else:
            print(f"\nWeek 1: NOT FOUND")

        if week2:
            print(f"\nWeek 2 details:")
            print(f"  rollover_applied: {week2.rollover_applied}")
            print(f"  dates: {week2.start_date} to {week2.end_date}")
        else:
            print(f"\nWeek 2: NOT FOUND")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    check_weeks_12()