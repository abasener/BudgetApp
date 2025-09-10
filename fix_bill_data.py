#!/usr/bin/env python3
"""Fix bill data with realistic typical amounts"""

from services.transaction_manager import TransactionManager

def fix_bills():
    tm = TransactionManager()
    
    # Define realistic typical amounts for existing bills
    bill_amounts = {
        "Rent": 1200.00,
        "School Loan": 450.00, 
        "Car Insurance": 120.00,
        "Phone": 80.00,
        "Internet": 60.00,
        "Taxes": 300.00,
        "apple": 100.00  # Keep existing
    }
    
    bills = tm.get_all_bills()
    print(f"Updating {len(bills)} bills with realistic typical amounts...")
    
    for bill in bills:
        if bill.name in bill_amounts and bill.typical_amount == 0:
            # Update typical amount
            new_amount = bill_amounts[bill.name]
            
            # Update the bill directly in the database
            bill.typical_amount = new_amount
            tm.db.commit()
            
            print(f"Updated {bill.name}: typical_amount = ${new_amount:.2f}")
            
            # Calculate new percentage
            percentage = min(100, (bill.running_total / bill.typical_amount) * 100) if bill.typical_amount > 0 else 0
            print(f"  New progress: {percentage:.1f}%")
    
    print("\nFinal bill status:")
    bills = tm.get_all_bills()  # Refresh
    for bill in bills[:7]:  # Show first 7 (matching max rings)
        percentage = min(100, (bill.running_total / bill.typical_amount) * 100) if bill.typical_amount > 0 else 0
        print(f"  {bill.name}: {percentage:.1f}% (${bill.running_total:.2f} / ${bill.typical_amount:.2f})")

if __name__ == "__main__":
    fix_bills()