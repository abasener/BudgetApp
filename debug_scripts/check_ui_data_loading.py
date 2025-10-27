"""
Check if the UI can properly load the rebuilt balance history data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def check_ui_data_loading():
    """Check if balance history data is accessible for UI"""
    print("=== CHECKING UI DATA LOADING ===")

    tm = TransactionManager()
    try:
        # Test the same way the weekly view would access data
        accounts = tm.get_all_accounts()
        weeks = tm.get_all_weeks()
        
        print(f"Found {len(accounts)} accounts and {len(weeks)} weeks")
        
        for account in accounts:
            print(f"\n{account.name}:")
            print(f"  running_total: ${account.running_total:.2f}")
            
            # Test get_balance_history_copy() method (used by UI)
            try:
                history = account.get_balance_history_copy()
                print(f"  get_balance_history_copy() works: {history is not None}")
                if history:
                    print(f"  history length: {len(history)}")
                    print(f"  first 3: {[f'${v:.2f}' for v in history[:3]]}")
                    print(f"  last 3: {[f'${v:.2f}' for v in history[-3:]]}")
                else:
                    print(f"  history is None or empty!")
            except Exception as e:
                print(f"  ERROR calling get_balance_history_copy(): {e}")
                
            # Test direct balance_history access
            try:
                direct_history = account.balance_history
                print(f"  direct balance_history access: {direct_history is not None}")
                if direct_history:
                    print(f"  direct history type: {type(direct_history)}")
                    print(f"  direct history length: {len(direct_history)}")
                else:
                    print(f"  direct balance_history is None!")
            except Exception as e:
                print(f"  ERROR accessing balance_history directly: {e}")

        # Test if weekly view style calculation would work
        print(f"\n=== TESTING WEEKLY VIEW CALCULATION ===")
        safety_account = next((a for a in accounts if a.name == "Safety Saving"), None)
        if safety_account:
            try:
                current_pay_period_index = 24  # Test period 24
                history = safety_account.get_balance_history_copy()
                
                if history and len(history) > current_pay_period_index:
                    starting_index = current_pay_period_index - 1
                    final_index = current_pay_period_index
                    
                    starting_balance = history[starting_index]
                    final_balance = history[final_index]
                    amount_change = final_balance - starting_balance
                    
                    print(f"Pay period {current_pay_period_index} would show:")
                    print(f"  Starting: ${starting_balance:.2f}")
                    print(f"  Final: ${final_balance:.2f}")  
                    print(f"  Amount change: ${amount_change:.2f}")
                    print(f"  Calculation: WORKING")
                else:
                    print(f"Insufficient history data for period {current_pay_period_index}")
                    print(f"History length: {len(history) if history else 0}")
            except Exception as e:
                print(f"Weekly calculation test failed: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    check_ui_data_loading()
