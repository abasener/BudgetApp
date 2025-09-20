"""
Transaction Manager - CRUD operations for all database entities
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from models import get_db, Account, Bill, Week, Transaction, TransactionType, AccountHistoryManager


class TransactionManager:
    def __init__(self):
        self.db = get_db()
        self.history_manager = AccountHistoryManager(self.db)
        from models.database import DATABASE_URL
        self._disable_auto_rollover = False  # Flag to disable automatic rollover recalculation
    
    def close(self):
        """Close database connection"""
        self.db.close()
    
    # Account operations
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return self.db.query(Account).all()
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID"""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_default_savings_account(self) -> Optional[Account]:
        """Get the default savings account"""
        return self.db.query(Account).filter(Account.is_default_save == True).first()
    
    def add_account(self, name: str, goal_amount: float = 0.0, auto_save_amount: float = 0.0,
                    is_default_save: bool = False, initial_balance: float = 0.0) -> Account:
        """Add a new savings account with optional initial balance"""
        # If this is being set as default, remove default from all others first
        if is_default_save:
            self.db.query(Account).update({Account.is_default_save: False})

        # If no accounts exist and this isn't being set as default, make it default
        existing_accounts = self.get_all_accounts()
        if not existing_accounts and not is_default_save:
            is_default_save = True

        # Create new account (no running_total field needed)
        account = Account(
            name=name,
            goal_amount=goal_amount,
            auto_save_amount=auto_save_amount,
            is_default_save=is_default_save
        )

        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        # Initialize AccountHistory with starting balance using a reasonable start date
        # Use a date well in the past so transactions will naturally come after it
        from datetime import datetime
        start_date = date(2024, 1, 1)  # Start of year for initial balance
        account.initialize_history(self.db, starting_balance=initial_balance, start_date=start_date)
        self.db.commit()

        return account
    
    def set_default_savings_account(self, account_id: int):
        """Set an account as the default savings account (removes default from others)"""
        # First, remove default flag from all accounts
        self.db.query(Account).update({Account.is_default_save: False})
        
        # Then set the specified account as default
        account = self.get_account_by_id(account_id)
        if account:
            account.is_default_save = True
            self.db.commit()
            return True
        return False
    
    def update_account_balance(self, account_id: int, new_balance: float):
        """Update account balance"""
        account = self.get_account_by_id(account_id)
        if account:
            account.running_total = new_balance
            self.db.commit()

    def update_account_with_transaction(self, account_id: int, transaction_amount: float, week_number: int):
        """Update account balance and balance history when a transaction is added"""
        account = self.get_account_by_id(account_id)
        if account:
            # Convert week number to pay period index (0-based)
            pay_period_index = (week_number - 1) // 2 + 1  # +1 because index 0 is starting balance

            # Use the new balance history update method
            account.update_balance_with_transaction(transaction_amount, pay_period_index)
            self.db.commit()

    def ensure_all_accounts_have_consistent_history(self):
        """Ensure all accounts have the same balance history length"""
        accounts = self.get_all_accounts()
        weeks = self.get_all_weeks()

        if not weeks:
            return

        # Calculate required history length: pay periods + 1 for starting balance
        max_week = max(w.week_number for w in weeks)
        required_length = (max_week - 1) // 2 + 2  # +2 because: +1 for pay period, +1 for starting

        for account in accounts:
            account.ensure_history_length(required_length)

        self.db.commit()
    
    # Bill operations
    def get_all_bills(self) -> List[Bill]:
        """Get all bills"""
        return self.db.query(Bill).all()

    def get_bill_by_id(self, bill_id: int) -> Optional[Bill]:
        """Get bill by ID"""
        return self.db.query(Bill).filter(Bill.id == bill_id).first()

    def add_bill(self, name: str, bill_type: str, payment_frequency: str, typical_amount: float,
                 amount_to_save: float, is_variable: bool = False, notes: str = None,
                 initial_balance: float = 0.0) -> Bill:
        """Add a new bill with AccountHistory initialization"""
        # Create new bill
        bill = Bill(
            name=name,
            bill_type=bill_type,
            payment_frequency=payment_frequency,
            typical_amount=typical_amount,
            amount_to_save=amount_to_save,
            is_variable=is_variable,
            notes=notes
        )

        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)

        # Initialize AccountHistory with starting balance using a reasonable start date
        # Use a date well in the past so transactions will naturally come after it
        start_date = date(2024, 1, 1)  # Start of year for initial balance
        bill.initialize_history(self.db, starting_balance=initial_balance, start_date=start_date)
        self.db.commit()

        return bill
    
    def get_bills_due_soon(self, days_ahead: int = 7) -> List[Bill]:
        """Get bills due within specified days"""
        target_date = date.today() + timedelta(days=days_ahead)
        return self.db.query(Bill).filter(Bill.next_payment_date <= target_date).all()
    
    def update_bill_payment(self, bill_id: int, payment_date: date, next_due_date: date):
        """Update bill after payment"""
        bill = self.get_bill_by_id(bill_id)
        if bill:
            bill.last_payment_date = payment_date
            bill.next_payment_date = next_due_date
            bill.running_total = 0.0  # Reset saved amount after payment
            self.db.commit()
    
    # Week operations
    def get_all_weeks(self) -> List[Week]:
        """Get all weeks ordered by week number"""
        return self.db.query(Week).order_by(asc(Week.week_number)).all()
    
    def get_week_by_number(self, week_number: int) -> Optional[Week]:
        """Get week by week number"""
        return self.db.query(Week).filter(Week.week_number == week_number).first()
    
    def get_current_week(self) -> Optional[Week]:
        """Get the current week (most recent)"""
        return self.db.query(Week).order_by(desc(Week.week_number)).first()
    
    def update_week_total(self, week_number: int, new_total: float):
        """Update week running total"""
        week = self.get_week_by_number(week_number)
        if week:
            week.running_total = new_total
            self.db.commit()

    def get_week_number_for_date(self, target_date: date) -> Optional[int]:
        """Get week number for a given date"""
        weeks = self.get_all_weeks()
        for week in weeks:
            if week.start_date <= target_date <= week.end_date:
                return week.week_number
        return None

    # Transaction operations
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """
        Add a new transaction and automatically create AccountHistory entries
        for any accounts affected by the transaction
        """
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        self.db.flush()  # Get transaction ID without committing

        # Automatically create AccountHistory entries for affected accounts
        if transaction.affects_account:
            change_amount = transaction.get_change_amount_for_account()
            if change_amount != 0:  # Only create history entry if there's an actual change
                self.history_manager.add_transaction_change(
                    account_id=transaction.affected_account_id,
                    account_type=transaction.account_type,
                    transaction_id=transaction.id,
                    change_amount=change_amount,
                    transaction_date=transaction.date
                )

        self.db.commit()
        self.db.refresh(transaction)

        # Trigger rollover recalculation for spending and saving transactions
        # but exclude rollover transactions to prevent infinite loops
        is_rollover_transaction = (
            transaction.description and
            ("rollover" in transaction.description.lower() or
             "end-of-period" in transaction.description.lower() or
             transaction.category == "Rollover" or
             transaction.category == "Rollover Deficit")
        )

        if (transaction.is_spending or transaction.is_saving) and not is_rollover_transaction and not self._disable_auto_rollover:
            self.trigger_rollover_recalculation(transaction.week_number)

        return transaction

    def set_auto_rollover_disabled(self, disabled: bool):
        """Enable or disable automatic rollover recalculation"""
        self._disable_auto_rollover = disabled
        if disabled:
            pass  # Rollover recalculation disabled
        else:
            pass  # Rollover recalculation enabled

    def trigger_rollover_recalculation(self, week_number: int):
        """Trigger rollover recalculation when transactions are added to a week"""
        try:
            from services.paycheck_processor import PaycheckProcessor
            processor = PaycheckProcessor()
            # Use the new dynamic recalculation system
            processor.recalculate_period_rollovers(week_number)
            processor.close()
        except Exception as e:
            print(f"Error triggering rollover recalculation: {e}")
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions"""
        return self.db.query(Transaction).order_by(desc(Transaction.date)).all()
    
    def get_transactions_by_week(self, week_number: int) -> List[Transaction]:
        """Get all transactions for a specific week"""
        return self.db.query(Transaction).filter(
            Transaction.week_number == week_number
        ).order_by(desc(Transaction.date)).all()
    
    def get_transactions_by_type(self, transaction_type: str, limit: Optional[int] = None) -> List[Transaction]:
        """Get transactions by type"""
        query = self.db.query(Transaction).filter(Transaction.transaction_type == transaction_type)
        query = query.order_by(desc(Transaction.date))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_spending_transactions(self, include_analytics_only: bool = False) -> List[Transaction]:
        """Get spending transactions, optionally filtered by analytics flag (excludes placeholder transactions)"""
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.transaction_type == TransactionType.SPENDING.value,
                Transaction.amount > 0  # Exclude $0 placeholder transactions
            )
        )
        
        if include_analytics_only:
            query = query.filter(Transaction.include_in_analytics == True)
        
        return query.order_by(desc(Transaction.date)).all()
    
    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> List[Transaction]:
        """Get transactions within date range"""
        return self.db.query(Transaction).filter(
            and_(Transaction.date >= start_date, Transaction.date <= end_date)
        ).order_by(desc(Transaction.date)).all()
    
    def get_transactions_by_category(self, category: str) -> List[Transaction]:
        """Get spending transactions by category (excludes placeholder transactions)"""
        return self.db.query(Transaction).filter(
            and_(
                Transaction.transaction_type == TransactionType.SPENDING.value,
                Transaction.category == category,
                Transaction.amount > 0,  # Exclude $0 placeholder transactions
                Transaction.include_in_analytics == True  # Only include analytics transactions
            )
        ).order_by(desc(Transaction.date)).all()
    
    def get_transactions_by_account(self, account_id: int, limit: Optional[int] = None) -> List[Transaction]:
        """Get transactions for a specific account"""
        query = self.db.query(Transaction).filter(Transaction.account_id == account_id).order_by(Transaction.date.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction and its AccountHistory entry"""
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            # Remove AccountHistory entry if it exists
            if transaction.affects_account:
                self.history_manager.delete_transaction_change(transaction_id)

            self.db.delete(transaction)
            self.db.commit()
            return True
        return False

    def update_transaction(self, transaction_id: int, updates: Dict[str, Any]) -> Optional[Transaction]:
        """Update a transaction and its AccountHistory entry"""
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            return None

        # Check if this update affects account relationships
        old_affects_account = transaction.affects_account
        old_change_amount = transaction.get_change_amount_for_account() if old_affects_account else 0
        old_account_id = transaction.affected_account_id if old_affects_account else None
        old_account_type = transaction.account_type if old_affects_account else None
        old_date = transaction.date

        # Apply updates
        for key, value in updates.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)

        # Handle AccountHistory changes
        new_affects_account = transaction.affects_account
        new_change_amount = transaction.get_change_amount_for_account() if new_affects_account else 0
        new_account_id = transaction.affected_account_id if new_affects_account else None
        new_account_type = transaction.account_type if new_affects_account else None
        new_date = transaction.date

        if old_affects_account and not new_affects_account:
            # Transaction no longer affects an account - remove history entry
            self.history_manager.delete_transaction_change(transaction_id)
        elif not old_affects_account and new_affects_account:
            # Transaction now affects an account - create history entry
            if new_change_amount != 0:
                self.history_manager.add_transaction_change(
                    account_id=new_account_id,
                    account_type=new_account_type,
                    transaction_id=transaction_id,
                    change_amount=new_change_amount,
                    transaction_date=new_date
                )
        elif old_affects_account and new_affects_account:
            # Transaction still affects an account - update history entry
            if (old_account_id != new_account_id or old_account_type != new_account_type):
                # Account changed - delete old and create new
                self.history_manager.delete_transaction_change(transaction_id)
                if new_change_amount != 0:
                    self.history_manager.add_transaction_change(
                        account_id=new_account_id,
                        account_type=new_account_type,
                        transaction_id=transaction_id,
                        change_amount=new_change_amount,
                        transaction_date=new_date
                    )
            else:
                # Same account - update existing entry
                self.history_manager.update_transaction_change(
                    transaction_id=transaction_id,
                    new_change_amount=new_change_amount,
                    new_date=new_date
                )

        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    # Analytics and summary methods
    def get_spending_by_category(self, include_analytics_only: bool = True) -> Dict[str, float]:
        """Get total spending by category (excludes placeholder transactions)"""
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.transaction_type == TransactionType.SPENDING.value,
                Transaction.amount > 0  # Exclude $0 placeholder transactions
            )
        )
        
        if include_analytics_only:
            query = query.filter(Transaction.include_in_analytics == True)
        
        transactions = query.all()
        
        category_totals = {}
        for transaction in transactions:
            category = transaction.category or "Uncategorized"
            category_totals[category] = category_totals.get(category, 0) + transaction.amount
            
        return category_totals
    
    def get_spending_by_week(self, include_analytics_only: bool = True) -> Dict[int, float]:
        """Get total spending by week (excludes placeholder transactions)"""
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.transaction_type == TransactionType.SPENDING.value,
                Transaction.amount > 0  # Exclude $0 placeholder transactions
            )
        )
        
        if include_analytics_only:
            query = query.filter(Transaction.include_in_analytics == True)
        
        transactions = query.all()
        
        week_totals = {}
        for transaction in transactions:
            week_num = transaction.week_number
            week_totals[week_num] = week_totals.get(week_num, 0) + transaction.amount
            
        return week_totals
    
    def get_income_vs_spending_summary(self) -> Dict[str, float]:
        """Get summary of income vs spending"""
        income_total = sum(t.amount for t in self.get_transactions_by_type("income"))
        spending_total = sum(t.amount for t in self.get_spending_transactions(include_analytics_only=True))
        bill_total = sum(t.amount for t in self.get_transactions_by_type("bill_pay"))
        saving_total = sum(t.amount for t in self.get_transactions_by_type("saving"))
        
        return {
            "total_income": income_total,
            "total_spending": spending_total,
            "total_bills": bill_total,
            "total_savings": saving_total,
            "net_difference": income_total - spending_total - bill_total
        }
    
    def get_week_summary(self, week_number: int) -> Dict[str, Any]:
        """Get detailed summary for a specific week"""
        week = self.get_week_by_number(week_number)
        if not week:
            return {}
        
        transactions = self.get_transactions_by_week(week_number)
        
        summary = {
            "week": week,
            "transactions": transactions,
            "total_income": sum(t.amount for t in transactions if t.is_income),
            "total_spending": sum(t.amount for t in transactions if t.is_spending and t.include_in_analytics),
            "total_bills": sum(t.amount for t in transactions if t.is_bill_pay),
            "total_savings": sum(t.amount for t in transactions if t.is_saving),
            "transaction_count": len(transactions)
        }
        
        return summary
    
    # Category management methods
    def get_all_categories(self) -> List[str]:
        """Get all unique categories from transactions"""
        try:
            # Query all unique categories from transactions
            categories = self.db.query(Transaction.category).filter(
                Transaction.category.isnot(None),
                Transaction.category != ""
            ).distinct().all()
            
            # Extract category names and sort them
            category_list = [cat[0] for cat in categories if cat[0]]
            category_list.sort(key=str.lower)
            
            return category_list
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def add_category(self, category_name: str) -> bool:
        """Add a new category by creating a placeholder transaction
        
        Note: This creates a $0 spending transaction with the new category
        to register it in the database. This ensures the category appears
        in all dropdowns and lists throughout the app.
        """
        try:
            if not category_name or not category_name.strip():
                return False
            
            category_name = category_name.strip()
            
            # Check if category already exists
            existing_categories = self.get_all_categories()
            if category_name.lower() in [cat.lower() for cat in existing_categories]:
                print(f"Category '{category_name}' already exists")
                return False
            
            # Get current week number for the transaction
            current_week = self.get_current_week()
            week_number = current_week.week_number if current_week else 1
            
            # Create a placeholder transaction with $0 amount to register the category
            placeholder_transaction = Transaction(
                date=datetime.now().date(),
                amount=0.0,
                description=f"Category placeholder: {category_name}",
                category=category_name,
                transaction_type=TransactionType.SPENDING.value,
                week_number=week_number,
                account_id=None,  # No specific account
                include_in_analytics=False  # Don't include in analytics
            )
            
            self.db.add(placeholder_transaction)
            self.db.commit()
            
            print(f"Successfully added category: {category_name}")
            return True
            
        except Exception as e:
            print(f"Error adding category: {e}")
            self.db.rollback()
            return False
    
    def remove_category(self, category_to_remove: str, replacement_category: str) -> bool:
        """Remove a category and reassign all its transactions to another category
        
        Args:
            category_to_remove: The category to remove
            replacement_category: The category to reassign transactions to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not category_to_remove or not replacement_category:
                return False
            
            if category_to_remove == replacement_category:
                print("Cannot replace a category with itself")
                return False
            
            # Get all categories to validate inputs
            existing_categories = self.get_all_categories()
            if category_to_remove not in existing_categories:
                print(f"Category '{category_to_remove}' does not exist")
                return False
            
            if replacement_category not in existing_categories:
                print(f"Replacement category '{replacement_category}' does not exist")
                return False
            
            # Get all transactions with the category to remove
            transactions_to_update = self.db.query(Transaction).filter(
                Transaction.category == category_to_remove
            ).all()
            
            print(f"Found {len(transactions_to_update)} transactions to reassign")
            
            # Update all transactions to use the replacement category
            for transaction in transactions_to_update:
                transaction.category = replacement_category
            
            # Commit all changes
            self.db.commit()
            
            print(f"Successfully removed category '{category_to_remove}' and reassigned {len(transactions_to_update)} transactions to '{replacement_category}'")
            return True
            
        except Exception as e:
            print(f"Error removing category: {e}")
            self.db.rollback()
            return False