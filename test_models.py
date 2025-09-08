"""
Quick test of database models
"""

from models import create_tables, get_db, Account, Bill, Week, Transaction, TransactionType
from datetime import date


def test_models():
    # Create tables
    print("Creating database tables...")
    create_tables()
    
    # Get database session
    db = get_db()
    
    try:
        # Test Account creation
        checking = Account(name="Checking", running_total=1500.00, is_default_save=True)
        savings = Account(name="Emergency Fund", running_total=5000.00, is_default_save=False)
        
        db.add(checking)
        db.add(savings)
        db.commit()
        
        print(f"Created accounts: {checking}, {savings}")
        
        # Test Bill creation
        rent = Bill(
            name="Rent",
            bill_type="Housing",
            days_between_payments=30,
            amount_to_save=800.00,
            amount_to_pay=800.00,
            running_total=0.00
        )
        
        db.add(rent)
        db.commit()
        
        print(f"Created bill: {rent}")
        
        # Test Week creation
        week1 = Week(
            week_number=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            running_total=500.00
        )
        
        db.add(week1)
        db.commit()
        
        print(f"Created week: {week1}")
        
        # Test Transaction creation
        spending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=1,
            amount=25.50,
            date=date(2024, 1, 2),
            description="Groceries",
            category="Food",
            include_in_analytics=True
        )
        
        abnormal_spending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=1,
            amount=15000.00,
            date=date(2024, 1, 3),
            description="Car purchase",
            category="Transportation", 
            include_in_analytics=False  # Exclude from analytics!
        )
        
        income = Transaction(
            transaction_type=TransactionType.INCOME.value,
            week_number=1,
            amount=1200.00,
            date=date(2024, 1, 1),
            description="Paycheck"
        )
        
        db.add(spending)
        db.add(abnormal_spending)
        db.add(income)
        db.commit()
        
        print(f"Created transactions:")
        print(f"  Normal spending: {spending}")
        print(f"  Abnormal spending: {abnormal_spending}")
        print(f"  Income: {income}")
        
        print("\nDatabase models test successful!")
        
    except Exception as e:
        print(f"Error testing models: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_models()