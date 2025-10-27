"""
Quick verification of generated sample data
"""

from models import get_db, Account, Bill, Week, Transaction


def verify_sample_data():
    db = get_db()
    
    try:
        # Count records
        accounts = db.query(Account).all()
        bills = db.query(Bill).all()
        weeks = db.query(Week).all()
        transactions = db.query(Transaction).all()
        
        print(f"Generated data summary:")
        print(f"  Accounts: {len(accounts)}")
        print(f"  Bills: {len(bills)}")
        print(f"  Weeks: {len(weeks)}")
        print(f"  Transactions: {len(transactions)}")
        
        # Show some sample records
        print(f"\nSample accounts:")
        for acc in accounts[:2]:
            print(f"  {acc}")
            
        print(f"\nSample transactions by type:")
        for tx_type in ["spending", "income", "bill_pay", "saving"]:
            count = db.query(Transaction).filter(Transaction.transaction_type == tx_type).count()
            sample = db.query(Transaction).filter(Transaction.transaction_type == tx_type).first()
            print(f"  {tx_type}: {count} transactions")
            if sample:
                print(f"    Example: {sample}")
                if tx_type == "spending":
                    analytics_true = db.query(Transaction).filter(
                        Transaction.transaction_type == tx_type,
                        Transaction.include_in_analytics == True
                    ).count()
                    analytics_false = db.query(Transaction).filter(
                        Transaction.transaction_type == tx_type,
                        Transaction.include_in_analytics == False
                    ).count()
                    print(f"    Include in analytics: {analytics_true} yes, {analytics_false} no")
        
    finally:
        db.close()


if __name__ == "__main__":
    verify_sample_data()