"""
Debug the relationship between savings transactions and balance history
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def debug_savings_vs_balance_history():
    """Debug savings transactions vs balance history"""
    print("=== DEBUGGING SAVINGS TRANSACTIONS VS BALANCE HISTORY ===")

    tm = TransactionManager()
    try:
        # Focus on Pay Period 24 discrepancy
        test_pay_period = 24
        week1_num = (test_pay_period - 1) * 2 + 1  # 47
        week2_num = week1_num + 1  # 48
        
        weeks = tm.get_all_weeks()
        week1 = next((w for w in weeks if w.week_number == week1_num), None)
        week2 = next((w for w in weeks if w.week_number == week2_num), None)
        
        if not (week1 and week2):
            print(f"Could not find weeks {week1_num} and {week2_num}")
            return
            
        print(f"Pay Period {test_pay_period}: Week {week1_num} ({week1.start_date} to {week1.end_date}) + Week {week2_num} ({week2.start_date} to {week2.end_date})")
        
        # Get all transactions in this period
        all_transactions = tm.get_all_transactions()
        period_transactions = [
            t for t in all_transactions 
            if week1.start_date <= t.date <= week2.end_date
        ]
        
        print(f"\nFound {len(period_transactions)} transactions in pay period {test_pay_period}")
        
        # Categorize transactions
        savings_transactions = [t for t in period_transactions if t.is_saving]
        spending_transactions = [t for t in period_transactions if t.is_spending]
        income_transactions = [t for t in period_transactions if t.is_income]
        
        print(f"\nTransaction breakdown:")
        print(f"  Income: {len(income_transactions)} transactions, total: ${sum(t.amount for t in income_transactions):.2f}")
        print(f"  Spending: {len(spending_transactions)} transactions, total: ${sum(t.amount for t in spending_transactions):.2f}")
        print(f"  Savings: {len(savings_transactions)} transactions, total: ${sum(t.amount for t in savings_transactions):.2f}")
        
        # Show savings transactions in detail
        print(f"\nSavings transactions in pay period {test_pay_period}:")
        savings_by_account = {}
        for t in savings_transactions:
            account_name = t.account.name if t.account else t.account_saved_to or "Unknown"
            if account_name not in savings_by_account:
                savings_by_account[account_name] = []
            savings_by_account[account_name].append(t)
            print(f"  {t.date}: ${t.amount:.2f} -> {account_name} ({t.description})")
        
        print(f"\nSavings by account:")
        for account_name, transactions in savings_by_account.items():
            total = sum(t.amount for t in transactions)
            print(f"  {account_name}: ${total:.2f} ({len(transactions)} transactions)")
        
        # Now check what balance history shows for this period
        print(f"\n=== BALANCE HISTORY FOR SAME PERIOD ===")
        
        safety_account = tm.db.query(Account).filter(Account.name == "Safety Saving").first()
        if safety_account:
            history = safety_account.get_balance_history_copy()
            
            starting_index = test_pay_period - 1  # 23
            final_index = test_pay_period  # 24
            
            if final_index < len(history):
                starting_balance = history[starting_index]
                final_balance = history[final_index]
                balance_change = final_balance - starting_balance
                
                print(f"Safety Saving balance history:")
                print(f"  Starting (index {starting_index}): ${starting_balance:.2f}")
                print(f"  Final (index {final_index}): ${final_balance:.2f}")
                print(f"  Change: ${balance_change:.2f}")
                
                # Compare with transaction total
                safety_transaction_total = savings_by_account.get("Safety Saving", [])
                safety_total = sum(t.amount for t in safety_transaction_total)
                
                print(f"\nComparison:")
                print(f"  Transactions to Safety Saving: ${safety_total:.2f}")
                print(f"  Balance history change: ${balance_change:.2f}")
                print(f"  Difference: ${safety_total - balance_change:.2f}")
                
                if abs(safety_total - balance_change) > 0.01:
                    print(f"  WARNING: Transactions don't match balance history!")
        
        # Calculate expected vs actual rollover
        print(f"\n=== ROLLOVER CALCULATION ===")
        total_income = sum(t.amount for t in income_transactions)
        total_spending = sum(t.amount for t in spending_transactions)
        total_savings = sum(t.amount for t in savings_transactions)
        
        expected_rollover = total_income - total_spending - total_savings
        
        # Get actual account changes (what UI shows as rollover)
        accounts = tm.get_all_accounts()
        total_account_changes = 0
        for account in accounts:
            history = account.get_balance_history_copy()
            if history and len(history) > test_pay_period:
                starting = history[test_pay_period - 1]
                final = history[test_pay_period]
                change = final - starting
                total_account_changes += change
        
        print(f"Expected rollover (income - spending - savings): ${expected_rollover:.2f}")
        print(f"Actual account changes (UI rollover): ${total_account_changes:.2f}")
        print(f"Rollover discrepancy: ${expected_rollover - total_account_changes:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_savings_vs_balance_history()
