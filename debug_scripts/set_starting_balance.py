"""
Set starting balance for Safety Saving account
"""

from services.transaction_manager import TransactionManager

def set_starting_balance():
    """Set Safety Saving account starting balance to $4204.01"""

    print("=== SETTING STARTING BALANCE ===")

    tm = TransactionManager()

    try:
        # Get default savings account
        default_savings = tm.get_default_savings_account()
        if default_savings:
            old_balance = default_savings.running_total
            default_savings.running_total = 4204.01
            default_savings.balance_history = [4204.01]  # Initialize with starting balance
            tm.db.commit()

            print(f"Safety Saving: ${old_balance:.2f} -> $4204.01")
            print(f"Balance history initialized: {default_savings.balance_history}")
            print("SUCCESS: Starting balance set!")
        else:
            print("ERROR: Default savings account not found")

    except Exception as e:
        print(f"ERROR: {e}")
        tm.db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    set_starting_balance()