"""
Debug why "Amount paid to Savings" shows "error loading savings data"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def debug_savings_display_error():
    """Debug the savings display error step by step"""
    print("=== DEBUGGING SAVINGS DISPLAY ERROR ===")

    tm = TransactionManager()
    try:
        # Test the exact same calculation as the UI does
        print("Step 1: Get accounts...")
        accounts = tm.get_all_accounts()
        print(f"Found {len(accounts)} accounts")
        
        print("\nStep 2: Test pay period index...")
        # Use a known pay period (24)
        current_pay_period_index = 24  # 1-based as used in UI
        print(f"Using pay period index: {current_pay_period_index}")
        
        print("\nStep 3: Test account balance calculations...")
        savings_text = ""
        
        for account in accounts:
            name = account.name[:14] + "..." if len(account.name) > 14 else account.name
            print(f"\nTesting {account.name}:")
            
            try:
                # Get balance history
                history = account.get_balance_history_copy()
                print(f"  History exists: {history is not None}")
                print(f"  History length: {len(history) if history else 0}")
                
                if not history:
                    print(f"  No history - using 0 change")
                    amount_change = 0.0
                else:
                    # Same indexing as UI
                    starting_index = current_pay_period_index - 1  # 23
                    final_index = current_pay_period_index  # 24
                    
                    print(f"  Indices: start={starting_index}, final={final_index}")
                    print(f"  History length check: {len(history)}")
                    
                    if starting_index < len(history):
                        starting_balance = history[starting_index]
                        print(f"  Starting balance: ${starting_balance:.2f}")
                    else:
                        starting_balance = history[-1] if history else account.running_total
                        print(f"  Starting balance (fallback): ${starting_balance:.2f}")
                    
                    if final_index < len(history):
                        final_balance = history[final_index]
                        print(f"  Final balance: ${final_balance:.2f}")
                    else:
                        final_balance = account.running_total
                        print(f"  Final balance (current): ${final_balance:.2f}")
                    
                    amount_change = final_balance - starting_balance
                    print(f"  Amount change: ${amount_change:.2f}")
                
                # Format like UI does
                amount_str = f"${amount_change:.0f}"
                savings_text += f"{name:<16} {amount_str:>10}\n"
                print(f"  Formatted: '{name:<16} {amount_str:>10}'")
                
            except Exception as e:
                print(f"  ERROR processing {account.name}: {e}")
                import traceback
                traceback.print_exc()
                raise e
        
        print(f"\nStep 4: Final result...")
        final_result = savings_text.rstrip() or "No accounts"
        print(f"Final savings text: '{final_result}'")
        print(f"Would display: {repr(final_result)}")
        
        # Test if this matches what UI should show
        print(f"\nStep 5: UI simulation...")
        print("This should match what savings_payments_label.setText() receives")
        
    except Exception as e:
        print(f"ERROR in simulation: {e}")
        import traceback
        traceback.print_exc()
        print("\nThis error might be why UI shows 'error loading savings data'")
    finally:
        tm.close()

if __name__ == "__main__":
    debug_savings_display_error()
