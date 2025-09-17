"""
Debug current bill running totals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Bill
from services.transaction_manager import TransactionManager

def debug_current_bills():
    """Check current bill running totals"""
    tm = TransactionManager()
    try:
        bills = tm.get_all_bills()

        print(f"=== CURRENT BILL RUNNING TOTALS ===")
        print(f"Found {len(bills)} bills:")

        for bill in bills:
            print(f"\n{bill.name}:")
            print(f"  running_total: ${bill.running_total:.2f}")
            print(f"  amount_to_save: ${bill.amount_to_save:.2f}")
            print(f"  typical_amount: ${bill.typical_amount:.2f}")
            print(f"  last_payment_amount: ${bill.last_payment_amount:.2f}")
            print(f"  last_payment_date: {bill.last_payment_date}")

            # Calculate percentage saved
            if bill.typical_amount > 0:
                percentage = (bill.running_total / bill.typical_amount) * 100
                print(f"  percentage saved: {percentage:.1f}%")

        # Also check if there are bill transactions
        print(f"\n=== BILL TRANSACTIONS ===")
        all_transactions = tm.get_all_transactions()
        bill_transactions = [t for t in all_transactions if t.is_bill_pay]

        print(f"Found {len(bill_transactions)} bill transactions:")
        for trans in bill_transactions[-10:]:  # Show last 10
            print(f"  {trans.date}: ${trans.amount:.2f} - {trans.description}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_current_bills()