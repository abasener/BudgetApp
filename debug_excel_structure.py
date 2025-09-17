"""
Debug the Excel file structure to understand the table layout
"""

import pandas as pd
import os

def debug_excel_structure():
    """Debug the Excel file structure"""

    excel_file = "TestData/Data2.xlsx"
    if not os.path.exists(excel_file):
        print(f"ERROR: File not found: {excel_file}")
        return

    print(f"=== DEBUGGING EXCEL STRUCTURE ===")
    print(f"File: {excel_file}")

    try:
        # Read the entire sheet without headers
        full_df = pd.read_excel(excel_file, sheet_name=0, header=None)
        print(f"Full sheet shape: {full_df.shape}")
        print(f"Columns: {full_df.shape[1]}")

        # Show the first 20 rows to understand structure
        print(f"\n=== FIRST 20 ROWS ===")
        for idx in range(min(20, len(full_df))):
            row_values = []
            for col in range(min(8, full_df.shape[1])):  # Show first 8 columns
                value = full_df.iloc[idx, col]
                if pd.isna(value):
                    row_values.append("NaN")
                else:
                    row_values.append(str(value)[:20])  # Truncate long values
            print(f"Row {idx:2d}: {row_values}")

        # Look for table headers specifically
        print(f"\n=== SEARCHING FOR TABLE HEADERS ===")
        for idx in range(min(50, len(full_df))):
            for col in range(min(full_df.shape[1], 6)):
                value = full_df.iloc[idx, col]
                if not pd.isna(value):
                    value_str = str(value).lower()
                    if any(keyword in value_str for keyword in ["start", "pay", "date", "amount", "category"]):
                        print(f"Row {idx}, Col {col}: '{value}' (potential header)")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel_structure()