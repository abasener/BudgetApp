#!/usr/bin/env python3
"""Debug script to check bill data"""

from services.transaction_manager import TransactionManager

def debug_bills():
    tm = TransactionManager()
    
    # Check bills
    bills = tm.get_all_bills()
    print(f"Found {len(bills)} bills:")
    
    if not bills:
        print("No bills found! Creating sample bills...")
        
        # Add sample bills
        sample_bills = [
            {"name": "Rent", "bill_type": "Housing", "payment_frequency": "monthly", 
             "typical_amount": 1200.0, "amount_to_save": 600.0, "running_total": 0.0},
            {"name": "Car Payment", "bill_type": "Transportation", "payment_frequency": "monthly",
             "typical_amount": 350.0, "amount_to_save": 175.0, "running_total": 0.0},
            {"name": "School", "bill_type": "Education", "payment_frequency": "semester",
             "typical_amount": 5000.0, "amount_to_save": 416.67, "running_total": 0.0},
            {"name": "Car Insurance", "bill_type": "Insurance", "payment_frequency": "monthly",
             "typical_amount": 150.0, "amount_to_save": 75.0, "running_total": 0.0}
        ]
        
        for bill_data in sample_bills:
            bill = tm.add_bill(bill_data)
            print(f"Created bill: {bill}")
    else:
        for bill in bills:
            print(f"  {bill.name}: running_total=${bill.running_total:.2f}, typical_amount=${bill.typical_amount:.2f}")
            percentage = min(100, (bill.running_total / bill.typical_amount) * 100) if bill.typical_amount > 0 else 0
            print(f"    Progress: {percentage:.1f}%")

if __name__ == "__main__":
    debug_bills()