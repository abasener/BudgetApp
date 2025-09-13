"""
Test script for rollover logic functionality
"""

from datetime import date, timedelta
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction, TransactionType, create_tables

def test_rollover_logic():
    """Test the rollover logic with sample data"""
    
    print("Testing Rollover Logic")
    print("=" * 50)
    
    # Initialize services
    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()
    
    try:
        # Create test weeks
        db = get_db()
        
        # Test Week 1 (should rollover to Week 2)
        test_week1 = Week(
            week_number=101,
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() - timedelta(days=8),
            running_total=500.0,  # Allocated $500
            rollover_applied=False
        )
        
        # Test Week 2 (should rollover to savings)
        test_week2 = Week(
            week_number=102,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() - timedelta(days=1),
            running_total=500.0,  # Allocated $500
            rollover_applied=False
        )
        
        # Add weeks to database
        db.add(test_week1)
        db.add(test_week2)
        db.commit()
        
        print(f"Created test weeks: {test_week1.week_number}, {test_week2.week_number}")
        
        # Add some spending transactions for Week 1 (spend $350 out of $500)
        week1_transaction = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week1.week_number,
            amount=350.0,
            date=test_week1.start_date + timedelta(days=2),
            description="Test spending for Week 1",
            category="Food"
        )
        
        # Add some spending transactions for Week 2 (spend $400 out of $500)
        week2_transaction = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week2.week_number,
            amount=400.0,
            date=test_week2.start_date + timedelta(days=2),
            description="Test spending for Week 2",
            category="Utilities"
        )
        
        db.add(week1_transaction)
        db.add(week2_transaction)
        db.commit()
        
        print(f"Added test transactions:")
        print(f"  Week {test_week1.week_number}: Spent $350 out of $500 (surplus $150)")
        print(f"  Week {test_week2.week_number}: Spent $400 out of $500 (surplus $100)")
        
        # Test rollover calculations
        print("\nCalculating rollovers...")
        
        rollover1 = paycheck_processor.calculate_week_rollover(test_week1.week_number)
        print(f"Week {rollover1.week_number} rollover: ${rollover1.rollover_amount:.2f}")
        
        rollover2 = paycheck_processor.calculate_week_rollover(test_week2.week_number)
        print(f"Week {rollover2.week_number} rollover: ${rollover2.rollover_amount:.2f}")
        
        # Test automatic rollover processing
        print("\nProcessing rollovers automatically...")
        
        processed = paycheck_processor.check_and_process_rollovers()
        print(f"Rollover processing completed: {processed}")
        
        # Verify results
        print("\nVerifying results...")
        
        # Check if Week 1 rollover was added to Week 2
        updated_week2 = transaction_manager.get_week_by_number(test_week2.week_number)
        print(f"Week {test_week2.week_number} running total after rollover: ${updated_week2.running_total:.2f}")
        print(f"Expected: ${test_week2.running_total + rollover1.rollover_amount:.2f}")
        
        # Check if rollover_applied flags were set
        updated_week1 = transaction_manager.get_week_by_number(test_week1.week_number)
        print(f"Week {test_week1.week_number} rollover_applied: {updated_week1.rollover_applied}")
        print(f"Week {test_week2.week_number} rollover_applied: {updated_week2.rollover_applied}")
        
        # Check savings account balance (Week 2 surplus should go to auto-save account)
        accounts = transaction_manager.get_all_accounts()
        auto_save_account = None
        for account in accounts:
            if hasattr(account, 'auto_save_amount') and account.auto_save_amount > 0:
                auto_save_account = account
                break
        
        if auto_save_account:
            print(f"Auto-save account balance: ${auto_save_account.running_total:.2f}")
        else:
            print("No auto-save account found - checking default savings account")
            default_savings = transaction_manager.get_default_savings_account()
            if default_savings:
                print(f"Default savings account balance: ${default_savings.running_total:.2f}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test data
        try:
            # Delete test transactions
            db.query(Transaction).filter(Transaction.week_number.in_([101, 102])).delete()
            # Delete test weeks
            db.query(Week).filter(Week.week_number.in_([101, 102])).delete()
            db.commit()
            print("\nTest data cleaned up")
        except:
            pass
        
        # Close connections
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_rollover_logic()