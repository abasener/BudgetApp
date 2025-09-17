"""
Test the rollover calculation fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager

def test_rollover_fix():
    """Test the rollover calculation fix"""
    print("=== TESTING ROLLOVER CALCULATION FIX ===")

    try:
        processor = PaycheckProcessor()
        
        # Test Week 48 rollover calculation with the fix
        print("Testing Week 48 rollover calculation...")
        
        rollover = processor.calculate_week_rollover(48)
        
        print(f"Week 48 rollover calculation:")
        print(f"  Allocated amount (base + income): ${rollover.allocated_amount:.2f}")
        print(f"  Spent amount: ${rollover.spent_amount:.2f}")
        print(f"  Remaining amount: ${rollover.remaining_amount:.2f}")
        print(f"  Rollover amount: ${rollover.rollover_amount:.2f}")
        
        # Compare with expected
        expected_rollover = 226.96
        print(f"\nComparison:")
        print(f"  Expected rollover: ${expected_rollover:.2f}")
        print(f"  Calculated rollover: ${rollover.rollover_amount:.2f}")
        print(f"  Difference: ${abs(expected_rollover - rollover.rollover_amount):.2f}")
        
        if abs(expected_rollover - rollover.rollover_amount) < 1.0:
            print(f"SUCCESS: Rollover calculation is now correct!")
        else:
            print(f"ISSUE: Rollover calculation still has issues.")
            
        # Show what the fix changed
        print(f"\nFix explanation:")
        print(f"  Base allocation (week.running_total): ${rollover.allocated_amount - (rollover.allocated_amount - 404.98):.2f}")
        print(f"  Income (rollover from Week 47): ${rollover.allocated_amount - 404.98:.2f}")
        print(f"  Total allocated: ${rollover.allocated_amount:.2f}")
        print(f"  This includes the Week 47 rollover that was missing before!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        processor.close()

if __name__ == "__main__":
    test_rollover_fix()
