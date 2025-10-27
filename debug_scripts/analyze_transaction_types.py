"""
Analyze current transaction types vs intended transaction flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Transaction
from services.transaction_manager import TransactionManager

def analyze_transaction_types():
    """Analyze current transaction types and their usage"""
    print("=== ANALYZING TRANSACTION TYPES ===")

    tm = TransactionManager()
    try:
        # Get all transactions
        all_transactions = tm.get_all_transactions()
        print(f"Total transactions: {len(all_transactions)}")
        
        # Group by transaction type
        by_type = {}
        for t in all_transactions:
            t_type = t.transaction_type
            if t_type not in by_type:
                by_type[t_type] = []
            by_type[t_type].append(t)
        
        print(f"\nTransaction types found:")
        for t_type, transactions in by_type.items():
            print(f"  {t_type}: {len(transactions)} transactions")
        
        # Analyze each type in detail
        for t_type, transactions in by_type.items():
            print(f"\n=== {t_type.upper()} TRANSACTIONS ===")
            print(f"Count: {len(transactions)}")
            
            # Show samples
            print("Sample transactions:")
            for t in transactions[:5]:
                target = "Unknown"
                if t.account_id and t.account:
                    target = f"Account: {t.account.name}"
                elif t.bill_id and t.bill:
                    target = f"Bill: {t.bill.name}"
                elif t.account_saved_to:
                    target = f"Account: {t.account_saved_to}"
                
                print(f"  {t.date}: ${t.amount:.2f} -> {target}")
                print(f"    Description: {t.description}")
                print(f"    Properties: account_id={t.account_id}, bill_id={t.bill_id}, account_saved_to='{t.account_saved_to}'")
        
        # Focus on the problematic savings from Pay Period 24
        print(f"\n=== PAY PERIOD 24 SAVINGS ANALYSIS ===")
        
        # Get weeks 47-48 date range
        weeks = tm.get_all_weeks()
        week47 = next((w for w in weeks if w.week_number == 47), None)
        week48 = next((w for w in weeks if w.week_number == 48), None)
        
        if week47 and week48:
            period_transactions = [
                t for t in all_transactions 
                if week47.start_date <= t.date <= week48.end_date and t.is_saving
            ]
            
            print(f"Savings transactions in Pay Period 24:")
            for t in period_transactions:
                print(f"  {t.date}: ${t.amount:.2f}")
                print(f"    Description: {t.description}")
                print(f"    Type: {t.transaction_type}")
                print(f"    account_id: {t.account_id}")
                print(f"    bill_id: {t.bill_id}")
                print(f"    account_saved_to: '{t.account_saved_to}'")
                print(f"    Is bill savings: {t.bill_id is not None}")
                print(f"    Is account savings: {t.account_id is not None}")
                print()
        
        # Check what your intended flow should be
        print(f"\n=== YOUR INTENDED TRANSACTION FLOW ===")
        print("1. Week to Outside (spending) - spending transactions with categories")
        print("2. Week to Bills (bill deposits) - money allocated to bills for future payment")
        print("3. Week to Savings (savings deposits) - money allocated to savings accounts")
        print("4. Bill to Outside (bill payment) - paying off a bill with saved amount")
        
        print(f"\n=== CURRENT VS INTENDED ===")
        
        # Analyze if current types match your intent
        spending_count = len(by_type.get('spending', []))
        saving_count = len(by_type.get('saving', []))
        income_count = len(by_type.get('income', []))
        
        print(f"Current 'spending' transactions: {spending_count} (matches #1: Week to Outside)")
        print(f"Current 'saving' transactions: {saving_count} (should be #2+#3: Bills+Savings deposits)")
        print(f"Current 'income' transactions: {income_count} (paychecks)")
        
        # Check if we're missing bill payment transactions (#4)
        bill_payment_transactions = [t for t in all_transactions if t.transaction_type == 'spending' and 'bill' in (t.description or '').lower()]
        print(f"Potential bill payment transactions: {len(bill_payment_transactions)}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    analyze_transaction_types()
