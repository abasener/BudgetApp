"""
Test percentage-based bill savings in isolation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor

def test_percentage_bills():
    """Test percentage bill calculations"""
    print("=== TESTING PERCENTAGE-BASED BILLS ===\n")
    
    tm = TransactionManager()
    pp = PaycheckProcessor()
    
    try:
        # Show existing bills
        existing_bills = tm.get_all_bills()
        print(f"Existing bills in database: {len(existing_bills)}")
        
        total_fixed = 0
        total_percentage = 0
        
        for bill in existing_bills:
            if 0 < bill.amount_to_save < 1:
                print(f"- {bill.name}: {bill.amount_to_save * 100:.1f}% (percentage-based)")
                total_percentage += bill.amount_to_save
            else:
                print(f"- {bill.name}: ${bill.amount_to_save:.2f} (fixed amount)")
                total_fixed += bill.amount_to_save
        
        print(f"\nTotals:")
        print(f"Fixed amount bills: ${total_fixed:.2f}")
        print(f"Percentage bills: {total_percentage * 100:.1f}% of paycheck")
        
        # Test with $1500 paycheck
        test_paycheck = 1500.00
        percentage_dollars = total_percentage * test_paycheck
        total_expected = total_fixed + percentage_dollars
        
        print(f"\nWith ${test_paycheck:.2f} paycheck:")
        print(f"Fixed bills: ${total_fixed:.2f}")
        print(f"Percentage bills: {total_percentage * 100:.1f}% = ${percentage_dollars:.2f}")
        print(f"Expected total: ${total_expected:.2f}")
        
        # Test actual calculation
        actual_deduction = pp.calculate_bills_deduction(test_paycheck)
        print(f"Actual calculation: ${actual_deduction:.2f}")
        
        if abs(actual_deduction - total_expected) < 0.01:
            print("SUCCESS: Percentage calculation is correct!")
        else:
            print(f"WARNING: Expected ${total_expected:.2f}, got ${actual_deduction:.2f}")
        
    finally:
        tm.close()
        pp.close()

if __name__ == "__main__":
    test_percentage_bills()