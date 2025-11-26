from models import get_db, Transaction, TransactionType

db = get_db()
paychecks = db.query(Transaction).filter(Transaction.transaction_type == TransactionType.INCOME.value).all()

print(f'Found {len(paychecks)} paychecks')
for i, p in enumerate(paychecks):
    print(f'Paycheck {i+1}: ${p.amount:.2f} on {p.date}')

if paychecks:
    avg = sum(p.amount for p in paychecks) / len(paychecks)
    rounded_avg = round(avg / 100) * 100
    print(f'\nAverage: ${avg:.2f}')
    print(f'Rounded to nearest $100: ${rounded_avg:.2f}')
else:
    print('\nNo paychecks found, default will remain $1500')
