"""
Debug what transactions exist and their dates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def debug_transactions():
    """Debug transaction data"""
    print("=== DEBUGGING TRANSACTIONS ===")

    tm = TransactionManager()
    try:
        account = tm.db.query(Account).filter(Account.name == "Safety Saving").first()
        weeks = tm.get_all_weeks()
        
        if account:
            print(f"Safety Saving account ID: {account.id}")
            
            # Get transactions by account
            transactions = tm.get_transactions_by_account(account.id)
            print(f"Found {len(transactions)} transactions via account ID")
            
            # Show first few transactions
            for i, t in enumerate(transactions[:10]):
                print(f"  {i+1}: {t.date} - ${t.amount:.2f} - {t.description}")
            
            # Check week date ranges
            print(f"\nWeek date ranges:")
            for week in weeks[:5]:
                print(f"  Week {week.week_number}: {week.start_date} to {week.end_date}")
            
            # Check if transactions fall within week ranges
            print(f"\nChecking if transactions fall in pay period 1 (weeks 1-2):")
            week1 = next((w for w in weeks if w.week_number == 1), None)
            week2 = next((w for w in weeks if w.week_number == 2), None)
            
            if week1 and week2:
                period_start = week1.start_date
                period_end = week2.end_date
                print(f"  Period 1 range: {period_start} to {period_end}")
                
                period_transactions = [
                    t for t in transactions
                    if period_start <= t.date <= period_end
                ]
                print(f"  Transactions in period 1: {len(period_transactions)}")
                for t in period_transactions:
                    print(f"    {t.date}: ${t.amount:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_transactions()
