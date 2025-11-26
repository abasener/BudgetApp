#!/usr/bin/env python3
"""Add goals to existing accounts for testing progress bars"""

from services.transaction_manager import TransactionManager

def add_account_goals():
    tm = TransactionManager()
    
    # Check existing accounts
    accounts = tm.get_all_accounts()
    print(f"Found {len(accounts)} accounts:")
    
    if not accounts:
        print("No accounts found! Creating sample accounts...")
        
        # Add sample accounts with goals
        sample_accounts = [
            {"name": "Emergency Fund", "running_total": 1500.0, "goal_amount": 5000.0},
            {"name": "Vacation Fund", "running_total": 800.0, "goal_amount": 2000.0},
            {"name": "Car Fund", "running_total": 3200.0, "goal_amount": 8000.0},
            {"name": "Home Down Payment", "running_total": 12000.0, "goal_amount": 25000.0},
            {"name": "General Savings", "running_total": 750.0, "goal_amount": 0.0}  # No goal
        ]
        
        for account_data in sample_accounts:
            account = tm.add_account(account_data)
            goal_text = f" (goal: ${account_data['goal_amount']:.0f})" if account_data['goal_amount'] > 0 else " (no goal)"
            print(f"Created account: {account.name} - ${account.running_total:.2f}{goal_text}")
    else:
        # Update existing accounts with goals if they don't have them
        account_goals = {
            "Emergency Fund": 5000.0,
            "Vacation Fund": 2000.0, 
            "Car Fund": 8000.0,
            "Home Down Payment": 25000.0,
        }
        
        for account in accounts:
            if account.name in account_goals and account.goal_amount == 0:
                # Update goal amount
                new_goal = account_goals[account.name]
                account.goal_amount = new_goal
                tm.db.commit()
                print(f"Updated {account.name}: set goal to ${new_goal:.2f}")
            
            # Show current status
            goal_text = f" (goal: ${account.goal_amount:.0f})" if account.goal_amount > 0 else " (no goal)"
            progress = account.goal_progress_percent if account.goal_amount > 0 else 0
            print(f"  {account.name}: ${account.running_total:.2f}{goal_text} - {progress:.1f}% complete")

if __name__ == "__main__":
    add_account_goals()