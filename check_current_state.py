"""
Check current account balances and balance history
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def check_current_state():
    """Check current account balances and balance history"""
    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()

        for account in accounts:
            print(f'{account.name}:')
            print(f'  running_total: ${account.running_total:.2f}')
            history = account.get_balance_history_copy()
            print(f'  balance_history length: {len(history) if history else 0}')
            if history:
                print(f'  First 5: {history[:5]}')
                print(f'  Last 5: {history[-5:]}')
            print()

    finally:
        tm.close()

if __name__ == "__main__":
    check_current_state()