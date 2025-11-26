"""
Import real data from TestData/Data2.xlsx
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db

def import_real_data():
    """Import data from TestData/Data2.xlsx"""

    print("=== IMPORTING REAL DATA ===")

    # Check if file exists
    excel_file = "TestData/Data2.xlsx"
    if not os.path.exists(excel_file):
        print(f"ERROR: File not found: {excel_file}")
        return

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        # Read Excel file
        print(f"Reading Excel file: {excel_file}")

        # Both tables are side by side in row 0
        # Spending table: columns 0-3 (Date, Day, Category, Amount)
        # Paychecks table: columns 5-7 (Start date, Pay Date, Amount)

        # Read Spending table (columns 0-3)
        spending_df = pd.read_excel(excel_file, sheet_name=0, header=0, usecols=[0, 1, 2, 3])
        spending_df = spending_df.dropna(how='all')  # Remove empty rows
        print(f"Spending columns: {list(spending_df.columns)}")
        print(f"Spending shape: {spending_df.shape}")

        # Read Paychecks table (columns 5-7)
        paychecks_df = pd.read_excel(excel_file, sheet_name=0, header=0, usecols=[5, 6, 7])
        paychecks_df = paychecks_df.dropna(how='all')  # Remove empty rows
        print(f"Paychecks columns: {list(paychecks_df.columns)}")
        print(f"Paychecks shape: {paychecks_df.shape}")

        # Process Paychecks first
        print(f"\n=== PROCESSING PAYCHECKS ===")

        # Expected columns based on Excel structure
        paycheck_cols = list(paychecks_df.columns)
        print(f"Available paycheck columns: {paycheck_cols}")

        # Use exact column names from Excel (pandas renames duplicate columns)
        start_date_col = "Start date"
        pay_date_col = "Pay Date"
        amount_col = "Amount.1"  # pandas renamed the duplicate Amount column

        # Verify columns exist
        if start_date_col not in paycheck_cols or pay_date_col not in paycheck_cols or amount_col not in paycheck_cols:
            print(f"ERROR: Expected columns not found in paychecks")
            print(f"Expected: {[start_date_col, pay_date_col, amount_col]}")
            print(f"Available: {paycheck_cols}")
            return

        print(f"Using columns - Start: {start_date_col}, Pay: {pay_date_col}, Amount: {amount_col}")

        # Process each paycheck
        paycheck_count = 0
        for idx, row in paychecks_df.iterrows():
            if pd.isna(row[start_date_col]) or pd.isna(row[pay_date_col]) or pd.isna(row[amount_col]):
                continue

            start_date = pd.to_datetime(row[start_date_col]).date()
            pay_date = pd.to_datetime(row[pay_date_col]).date()
            amount = float(row[amount_col])

            print(f"Processing paycheck {paycheck_count + 1}: ${amount:.2f} from {start_date} to {pay_date}")

            # Add paycheck using paycheck processor
            try:
                paycheck_processor.process_new_paycheck(amount, pay_date, start_date)
                paycheck_count += 1
                print(f"  SUCCESS: Added paycheck successfully")
            except Exception as e:
                print(f"  ERROR: Error adding paycheck: {e}")

        print(f"Successfully processed {paycheck_count} paychecks")

        # Process Spending transactions
        print(f"\n=== PROCESSING SPENDING TRANSACTIONS ===")

        # Expected columns based on Excel structure
        spending_cols = list(spending_df.columns)
        print(f"Available spending columns: {spending_cols}")

        # Use exact column names from Excel
        date_col = "Date"
        category_col = "Catigorie"  # Note: typo in original Excel
        amount_col = "Amount"

        # Verify columns exist
        if date_col not in spending_cols or category_col not in spending_cols or amount_col not in spending_cols:
            print(f"ERROR: Expected columns not found in spending")
            print(f"Expected: {[date_col, category_col, amount_col]}")
            print(f"Available: {spending_cols}")
            return

        print(f"Using columns - Date: {date_col}, Category: {category_col}, Amount: {amount_col}")

        # Process each transaction
        transaction_count = 0
        negative_transaction_count = 0

        for idx, row in spending_df.iterrows():
            if pd.isna(row[date_col]) or pd.isna(row[category_col]) or pd.isna(row[amount_col]):
                continue

            transaction_date = pd.to_datetime(row[date_col]).date()
            category = str(row[category_col]).strip()
            amount = float(row[amount_col])

            # Determine which week this transaction belongs to
            week_number = transaction_manager.get_week_number_for_date(transaction_date)
            if week_number is None:
                print(f"  ⚠ Could not determine week for transaction on {transaction_date}, skipping")
                continue

            # Determine include_in_analytics flag
            include_in_analytics = amount >= 0  # Positive amounts are included in analytics/plotting
            if amount < 0:
                negative_transaction_count += 1
                print(f"  ANALYTICS: Negative transaction (${amount:.2f}) - excluded from analytics/plotting")

            # Create transaction
            transaction_data = {
                "transaction_type": "spending",
                "week_number": week_number,
                "amount": abs(amount),  # Store as positive value
                "date": transaction_date,
                "description": f"{category} transaction",
                "category": category,
                "include_in_analytics": include_in_analytics
            }

            try:
                transaction_manager.add_transaction(transaction_data)
                transaction_count += 1
                print(f"  SUCCESS: Added transaction: ${abs(amount):.2f} - {category} (Week {week_number})")
            except Exception as e:
                print(f"  ERROR: Error adding transaction: {e}")

        print(f"\nSuccessfully processed {transaction_count} transactions")
        print(f"  - {transaction_count - negative_transaction_count} positive transactions (included in analytics)")
        print(f"  - {negative_transaction_count} negative transactions (excluded from analytics)")

        # Summary
        print(f"\n=== IMPORT SUMMARY ===")
        print(f"SUCCESS: Imported {paycheck_count} paychecks")
        print(f"SUCCESS: Imported {transaction_count} spending transactions")
        print(f"SUCCESS: Created weeks and processed paycheck allocations")
        print(f"SUCCESS: Ready for testing!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    import_real_data()