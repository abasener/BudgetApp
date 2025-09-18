"""
Test the complete flow with the expected values using the fixed logic
"""

from services.paycheck_processor import PaycheckProcessor

def test_expected_flow():
    """Test the flow with your expected values"""

    print("=== TESTING EXPECTED FLOW ===")
    print("Input: $1500 paycheck")
    print("Expected deductions: $2417.50 (bills)")
    print("Expected remaining: $1500 - $2417.50 = -$917.00")
    print("Expected per week: -$917.00 / 2 = -$458.50")
    print()

    pp = PaycheckProcessor()

    try:
        # Test Week 53 calculation (current state)
        print("=== WEEK 53 CURRENT STATE ===")
        week53_rollover = pp.calculate_week_rollover(53)
        print(f"Week 53 allocated amount: ${week53_rollover.allocated_amount:.2f}")
        print(f"Week 53 spent amount: ${week53_rollover.spent_amount:.2f}")
        print(f"Week 53 remaining: ${week53_rollover.remaining_amount:.2f}")
        print(f"Week 53 rollover to Week 54: ${week53_rollover.rollover_amount:.2f}")
        print()

        # Test Week 54 calculation
        print("=== WEEK 54 CURRENT STATE ===")
        week54_rollover = pp.calculate_week_rollover(54)
        print(f"Week 54 base allocation: ${week54_rollover.allocated_amount:.2f}")
        print(f"Week 54 spent amount: ${week54_rollover.spent_amount:.2f}")
        print(f"Week 54 remaining: ${week54_rollover.remaining_amount:.2f}")
        print(f"Week 54 rollover to savings: ${week54_rollover.rollover_amount:.2f}")
        print()

        print("=== EXPECTED vs ACTUAL ===")
        print("Expected Week 53 starting: -$458.50")
        print(f"Actual Week 53 starting: ${week53_rollover.allocated_amount:.2f}")
        print("✅ MATCH!" if abs(week53_rollover.allocated_amount - (-458.50)) < 0.01 else "❌ MISMATCH!")
        print()

        print("Expected Week 54 starting: -$458.50")
        print(f"Actual Week 54 starting: ${week54_rollover.allocated_amount:.2f}")
        print("✅ MATCH!" if abs(week54_rollover.allocated_amount - (-458.50)) < 0.01 else "❌ MISMATCH!")
        print()

        print("Expected Week 53 rollover (no spending): -$458.50")
        print(f"Actual Week 53 rollover: ${week53_rollover.rollover_amount:.2f}")
        print("✅ MATCH!" if abs(week53_rollover.rollover_amount - (-458.50)) < 0.01 else "❌ MISMATCH!")
        print()

        # Week 54 should get -$458.50 (its base) + -$458.50 (rollover from Week 53) = -$917.00
        expected_week54_with_rollover = -458.50 + (-458.50)
        print(f"Expected Week 54 with rollover: ${expected_week54_with_rollover:.2f}")
        print(f"Expected Week 54 rollover to savings: ${expected_week54_with_rollover:.2f}")
        print(f"Actual Week 54 rollover to savings: ${week54_rollover.rollover_amount:.2f}")

        # Note: Week 54 rollover might be different if Week 53's rollover hasn't been applied yet

    finally:
        pp.close()

if __name__ == "__main__":
    test_expected_flow()