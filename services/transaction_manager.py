"""
Transaction Manager - CRUD operations for all database entities
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from models import get_db, Account, Bill, Week, Transaction, TransactionType


class TransactionManager:
    def __init__(self):
        self.db = get_db()
    
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
    
    def update_account_balance(self, account_id: int, new_balance: float):
        """Update account balance"""
        account = self.get_account_by_id(account_id)
        if account:
            account.running_total = new_balance
            self.db.commit()
    
    # Bill operations
    def get_all_bills(self) -> List[Bill]:
        """Get all bills"""
        return self.db.query(Bill).all()
    
    def get_bill_by_id(self, bill_id: int) -> Optional[Bill]:
        """Get bill by ID"""
        return self.db.query(Bill).filter(Bill.id == bill_id).first()
    
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
    
    # Transaction operations
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Add a new transaction"""
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
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
        """Get spending transactions, optionally filtered by analytics flag"""
        query = self.db.query(Transaction).filter(Transaction.transaction_type == TransactionType.SPENDING.value)
        
        if include_analytics_only:
            query = query.filter(Transaction.include_in_analytics == True)
        
        return query.order_by(desc(Transaction.date)).all()
    
    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> List[Transaction]:
        """Get transactions within date range"""
        return self.db.query(Transaction).filter(
            and_(Transaction.date >= start_date, Transaction.date <= end_date)
        ).order_by(desc(Transaction.date)).all()
    
    def get_transactions_by_category(self, category: str) -> List[Transaction]:
        """Get spending transactions by category"""
        return self.db.query(Transaction).filter(
            and_(
                Transaction.transaction_type == TransactionType.SPENDING.value,
                Transaction.category == category
            )
        ).order_by(desc(Transaction.date)).all()
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
            return True
        return False
    
    def update_transaction(self, transaction_id: int, updates: Dict[str, Any]) -> Optional[Transaction]:
        """Update a transaction"""
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            for key, value in updates.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        return None
    
    # Analytics and summary methods
    def get_spending_by_category(self, include_analytics_only: bool = True) -> Dict[str, float]:
        """Get total spending by category"""
        query = self.db.query(Transaction).filter(Transaction.transaction_type == TransactionType.SPENDING.value)
        
        if include_analytics_only:
            query = query.filter(Transaction.include_in_analytics == True)
        
        transactions = query.all()
        
        category_totals = {}
        for transaction in transactions:
            category = transaction.category or "Uncategorized"
            category_totals[category] = category_totals.get(category, 0) + transaction.amount
            
        return category_totals
    
    def get_spending_by_week(self, include_analytics_only: bool = True) -> Dict[int, float]:
        """Get total spending by week"""
        query = self.db.query(Transaction).filter(Transaction.transaction_type == TransactionType.SPENDING.value)
        
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