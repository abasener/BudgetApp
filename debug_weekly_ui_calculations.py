"""
Debug the weekly UI calculations to see what should be displayed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def debug_weekly_ui_calculations():
    """Debug weekly UI calculations step by step"""
    print("=== DEBUGGING WEEKLY UI CALCULATIONS ===")

    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()
        weeks = tm.get_all_weeks()
        
        # Test with a specific pay period (let's use period 24 as example)
        test_pay_period = 24
        print(f"Testing Pay Period {test_pay_period}")
        
        # Simulate what weekly view does
        current_pay_period_index = test_pay_period  # 1-based
        
        print(f"\n=== 1. ACCOUNT BALANCE CHANGES (Start vs Final) ===")
        account_changes = {}
        
        for account in accounts:
            print(f"\n{account.name}:")
            print(f"  Current running_total: ${account.running_total:.2f}")
            
            # Get balance history like the UI does
            history = account.get_balance_history_copy()
            
            if not history:
                print(f"  No history - would show $0.00 change")
                amount_change = 0.0
            else:
                # Use same indexing as weekly view
                starting_index = current_pay_period_index - 1  # 23
                final_index = current_pay_period_index  # 24
                
                print(f"  History length: {len(history)}")
                print(f"  Using indices: start={starting_index}, final={final_index}")
                
                if starting_index < len(history):
                    starting_balance = history[starting_index]
                else:
                    starting_balance = history[-1] if history else account.running_total
                    print(f"  WARNING: start index {starting_index} beyond history, using last value")
                
                if final_index < len(history):
                    final_balance = history[final_index]
                else:
                    final_balance = account.running_total
                    print(f"  WARNING: final index {final_index} beyond history, using current total")
                
                amount_change = final_balance - starting_balance
                
                print(f"  Starting balance (index {starting_index}): ${starting_balance:.2f}")
                print(f"  Final balance (index {final_index}): ${final_balance:.2f}")
                print(f"  Amount change: ${amount_change:.2f}")
            
            account_changes[account.name] = amount_change
        
        print(f"\n=== 2. AMOUNT PAID TO SAVINGS FORMATTING ===")
        savings_text = ""
        for account in accounts:
            name = account.name[:14] + "..." if len(account.name) > 14 else account.name
            amount_change = account_changes[account.name]
            amount_str = f"${amount_change:.0f}"
            savings_text += f"{name:<16} {amount_str:>10}\n"
            print(f"  {name}: {amount_str}")
        
        print(f"\nFormatted savings text:")
        print(f"'{savings_text.rstrip()}'")
        
        print(f"\n=== 3. ROLLOVER CALCULATION CHECK ===")
        # Check if rollover should match the account changes
        total_account_change = sum(account_changes.values())
        print(f"Total account changes: ${total_account_change:.2f}")
        
        # Get week data for this pay period to check rollover
        week1_num = (test_pay_period - 1) * 2 + 1  # 47
        week2_num = week1_num + 1  # 48
        
        week1 = next((w for w in weeks if w.week_number == week1_num), None)
        week2 = next((w for w in weeks if w.week_number == week2_num), None)
        
        if week1 and week2:
            print(f"\nWeeks for pay period {test_pay_period}:")
            print(f"  Week {week1_num}: {week1.start_date} to {week1.end_date}")
            print(f"  Week {week2_num}: {week2.start_date} to {week2.end_date}")
            
            # Get all transactions for this pay period
            all_transactions = tm.get_all_transactions()
            
            # Filter transactions by date range
            period_transactions = []
            for t in all_transactions:
                if week1.start_date <= t.date <= week2.end_date:
                    period_transactions.append(t)
            
            print(f"  Found {len(period_transactions)} transactions in this period")
            
            # Categorize transactions
            spending_total = 0
            savings_total = 0
            income_total = 0
            
            for t in period_transactions:
                if t.is_spending:
                    spending_total += t.amount
                elif t.is_saving:
                    savings_total += t.amount
                elif t.is_income:
                    income_total += t.amount
            
            print(f"\nTransaction totals for period:")
            print(f"  Income: ${income_total:.2f}")
            print(f"  Spending: ${spending_total:.2f}")
            print(f"  Savings: ${savings_total:.2f}")
            
            # Calculate expected rollover
            expected_rollover = income_total - spending_total - savings_total
            print(f"  Expected rollover: ${expected_rollover:.2f}")
            print(f"  Account changes: ${total_account_change:.2f}")
            print(f"  Difference: ${expected_rollover - total_account_change:.2f}")
        
        print(f"\n=== 4. POTENTIAL ISSUES ===")
        if not savings_text.strip():
            print("❌ ISSUE: savings_text is empty - this explains why 'Amount paid to savings' not showing")
        else:
            print("✅ savings_text has content")
            
        if abs(total_account_change) < 0.01:
            print("❌ ISSUE: All account changes are zero - balance history might still be broken")
        else:
            print("✅ Account changes are non-zero")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_weekly_ui_calculations()
