"""
Test the transaction manager functionality
"""

import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from services.transaction_manager import TransactionManager
from models import TransactionType


def test_transaction_manager():
    manager = TransactionManager()
    
    try:
        print("Testing Transaction Manager...")
        
        # Test account operations
        print("\n1. Account Operations:")
        accounts = manager.get_all_accounts()
        print(f"   Total accounts: {len(accounts)}")
        for acc in accounts:
            print(f"   {acc}")
        
        default_savings = manager.get_default_savings_account()
        print(f"   Default savings account: {default_savings}")
        
        # Test bill operations
        print("\n2. Bill Operations:")
        bills = manager.get_all_bills()
        print(f"   Total bills: {len(bills)}")
        for bill in bills[:3]:  # Show first 3
            print(f"   {bill}")
        
        # Test week operations
        print("\n3. Week Operations:")
        weeks = manager.get_all_weeks()
        print(f"   Total weeks: {len(weeks)}")
        current_week = manager.get_current_week()
        print(f"   Current week: {current_week}")
        
        # Test transaction operations
        print("\n4. Transaction Operations:")
        
        # Get spending with and without analytics filter
        all_spending = manager.get_spending_transactions(include_analytics_only=False)
        analytics_spending = manager.get_spending_transactions(include_analytics_only=True)
        print(f"   All spending transactions: {len(all_spending)}")
        print(f"   Analytics-eligible spending: {len(analytics_spending)}")
        print(f"   Abnormal transactions filtered out: {len(all_spending) - len(analytics_spending)}")
        
        # Test category analysis
        print("\n5. Analytics:")
        category_totals = manager.get_spending_by_category(include_analytics_only=True)
        print(f"   Spending by category (analytics only):")
        for category, total in sorted(category_totals.items()):
            print(f"     {category}: ${total:.2f}")
        
        # Test weekly spending
        week_totals = manager.get_spending_by_week(include_analytics_only=True)
        print(f"\n   Spending by week (first 5 weeks):")
        for week_num in sorted(list(week_totals.keys()))[:5]:
            total = week_totals[week_num]
            print(f"     Week {week_num}: ${total:.2f}")
        
        # Test overall summary
        summary = manager.get_income_vs_spending_summary()
        print(f"\n6. Financial Summary:")
        print(f"   Total Income: ${summary['total_income']:.2f}")
        print(f"   Total Spending: ${summary['total_spending']:.2f}")
        print(f"   Total Bills: ${summary['total_bills']:.2f}")
        print(f"   Total Savings: ${summary['total_savings']:.2f}")
        print(f"   Net Difference: ${summary['net_difference']:.2f}")
        
        # Test week summary
        if current_week:
            week_summary = manager.get_week_summary(current_week.week_number)
            print(f"\n7. Current Week ({current_week.week_number}) Summary:")
            print(f"   Income: ${week_summary['total_income']:.2f}")
            print(f"   Spending: ${week_summary['total_spending']:.2f}")
            print(f"   Bills: ${week_summary['total_bills']:.2f}")
            print(f"   Savings: ${week_summary['total_savings']:.2f}")
            print(f"   Total Transactions: {week_summary['transaction_count']}")
        
        print("\n✅ Transaction Manager test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing transaction manager: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.close()


if __name__ == "__main__":
    test_transaction_manager()