"""
Analyze the recent paycheck allocation to find the discrepancy
"""

from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction

def analyze_recent_paycheck():
    tm = TransactionManager()
    db = get_db()

    try:
        # Get the most recent paycheck
        print('=== RECENT PAYCHECK ANALYSIS ===')
        recent_paychecks = db.query(Transaction).filter(Transaction.description.like('%paycheck%')).order_by(Transaction.week_number.desc()).limit(3).all()

        for paycheck in recent_paychecks:
            print(f'Week {paycheck.week_number}: ${paycheck.amount:.2f} - {paycheck.description}')

        # Focus on week 53-54 which you mentioned
        print('\n=== WEEK 53-54 ANALYSIS ===')
        week53 = tm.get_week_by_number(53)
        week54 = tm.get_week_by_number(54)

        if week53:
            print(f'Week 53 running_total: ${week53.running_total:.2f}')
        if week54:
            print(f'Week 54 running_total: ${week54.running_total:.2f}')

        # Get paycheck from week 53
        week53_transactions = tm.get_transactions_by_week(53)
        for tx in week53_transactions:
            if 'paycheck' in tx.description.lower():
                print(f'Week 53 paycheck: ${tx.amount:.2f}')

                # Calculate deductions
                week53_savings = [t for t in week53_transactions if t.transaction_type == 'saving' and 'allocation' in t.description.lower()]
                total_deductions = sum(t.amount for t in week53_savings)
                print(f'Total bill/savings deductions: ${total_deductions:.2f}')
                print('Breakdown:')
                for saving_tx in week53_savings:
                    print(f'  {saving_tx.description}: ${saving_tx.amount:.2f}')

                remaining = tx.amount - total_deductions
                per_week = remaining / 2
                print(f'Remaining after deductions: ${remaining:.2f}')
                print(f'Per week allocation: ${per_week:.2f}')
                print(f'Expected Week 53: ${per_week:.2f}')
                print(f'Expected Week 54: ${per_week:.2f}')
                print(f'Actual Week 53: ${week53.running_total:.2f}')
                print(f'Actual Week 54: ${week54.running_total:.2f}')

    finally:
        tm.close()

if __name__ == "__main__":
    analyze_recent_paycheck()