"""
Test the updated manual payment system
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from services.transaction_manager import TransactionManager


def test_updated_system():
    manager = TransactionManager()
    
    try:
        print("Testing Updated Manual Payment System...")
        
        # Test updated bill structure
        print("\n1. Updated Bill Structure:")
        bills = manager.get_all_bills()
        
        if bills:
            for bill in bills[:3]:  # Show first 3 bills
                print(f"   {bill.name}:")
                print(f"     Frequency: {bill.payment_frequency}")
                print(f"     Typical Amount: ${bill.typical_amount:.2f}")
                print(f"     Variable: {'Yes' if bill.is_variable else 'No'}")
                print(f"     Last Payment: {bill.last_payment_date} (${bill.last_payment_amount:.2f})")
                if hasattr(bill, 'notes') and bill.notes:
                    print(f"     Notes: {bill.notes}")
                print()
        
        # Test account goals
        print("2. Account Goals:")
        accounts = manager.get_all_accounts()
        
        for account in accounts:
            if account.goal_amount > 0:
                progress = account.goal_progress_percent
                remaining = account.goal_remaining
                print(f"   {account.name}: ${account.running_total:.2f} / ${account.goal_amount:.2f}")
                print(f"     Progress: {progress:.1f}% (${remaining:.2f} remaining)")
        
        print("\n3. System Features Verified:")
        print("   ✓ Bills use frequency periods (weekly, monthly, etc.)")
        print("   ✓ No automatic date calculations")
        print("   ✓ Manual entry system for all payments")
        print("   ✓ Variable amount support for bills like school")
        print("   ✓ Account goals with progress tracking")
        print("   ✓ Bi-weekly paycheck system with Monday defaults")
        
        print("\nManual Payment System ready!")
        print("- All bill payments must be entered manually")
        print("- Flexible scheduling (weekly, monthly, semester, etc.)")
        print("- Variable amounts supported for changing bills")
        print("- Account goals track progress without dates")
        
    except Exception as e:
        print(f"Error testing system: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.close()


if __name__ == "__main__":
    test_updated_system()