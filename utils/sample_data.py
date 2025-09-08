"""
Sample data generator for testing the budget app
"""

import random
import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# Add parent directory to path so we can import models
sys.path.append(str(Path(__file__).parent.parent))

from models import (get_db, Account, Bill, Week, Transaction, TransactionType,
                   create_tables, drop_tables)


class SampleDataGenerator:
    def __init__(self):
        self.db = get_db()
        self.spending_categories = [
            "Food", "Transportation", "Entertainment", "Shopping", "Utilities",
            "Healthcare", "Personal Care", "Education", "Miscellaneous"
        ]
        
        self.bill_types = [
            ("Rent", "Housing", 30, 800.00),
            ("School Loan", "Education", 30, 250.00), 
            ("Car Insurance", "Transportation", 180, 120.00),
            ("Phone", "Utilities", 30, 65.00),
            ("Internet", "Utilities", 30, 45.00),
            ("Taxes", "Government", 90, 300.00)
        ]
        
    def generate_all_sample_data(self, weeks_back=12):
        """Generate comprehensive sample data"""
        print("Dropping existing tables...")
        drop_tables()
        
        print("Creating fresh tables...")
        create_tables()
        
        print("Generating accounts...")
        self.create_accounts()
        
        print("Generating bills...")
        self.create_bills()
        
        print("Generating weeks...")
        self.create_weeks(weeks_back)
        
        print("Generating transactions...")
        self.create_transactions(weeks_back)
        
        print(f"Sample data generation complete! Generated {weeks_back} weeks of data.")
        
    def create_accounts(self):
        """Create sample accounts"""
        accounts = [
            Account(name="Checking", running_total=1500.00, is_default_save=True),
            Account(name="Emergency Fund", running_total=5000.00, is_default_save=False),
            Account(name="Vacation Fund", running_total=800.00, is_default_save=False),
            Account(name="Car Fund", running_total=2500.00, is_default_save=False)
        ]
        
        for account in accounts:
            self.db.add(account)
        self.db.commit()
        
    def create_bills(self):
        """Create sample bills"""
        for name, bill_type, days_between, amount in self.bill_types:
            bill = Bill(
                name=name,
                bill_type=bill_type,
                days_between_payments=days_between,
                amount_to_save=amount / (days_between / 14),  # Save per bi-weekly period
                amount_to_pay=amount,
                running_total=random.uniform(0, amount * 0.8),  # Partial savings
                last_payment_date=date.today() - timedelta(days=random.randint(1, days_between)),
                next_payment_date=date.today() + timedelta(days=random.randint(1, days_between))
            )
            self.db.add(bill)
        self.db.commit()
        
    def create_weeks(self, weeks_back):
        """Create sample weeks (bi-weekly pay periods)"""
        today = date.today()
        
        for week_num in range(1, weeks_back + 1):
            # Calculate week start (go backwards from today)
            start_date = today - timedelta(days=(weeks_back - week_num + 1) * 7)
            end_date = start_date + timedelta(days=6)
            
            # Bi-weekly logic: every other week gets a paycheck boost
            base_amount = 600.00  # Base weekly spending money
            if week_num % 2 == 1:  # Paycheck weeks
                running_total = base_amount + random.uniform(50, 150)  # Extra from paycheck
            else:
                running_total = base_amount - random.uniform(0, 100)   # Rollover varies
                
            week = Week(
                week_number=week_num,
                start_date=start_date,
                end_date=end_date,
                running_total=running_total
            )
            self.db.add(week)
        
        self.db.commit()
        
    def create_transactions(self, weeks_back):
        """Create sample transactions for all weeks"""
        accounts = self.db.query(Account).all()
        bills = self.db.query(Bill).all()
        weeks = self.db.query(Week).all()
        
        for week in weeks:
            self.create_transactions_for_week(week, accounts, bills)
            
    def create_transactions_for_week(self, week, accounts, bills):
        """Create transactions for a specific week"""
        week_start = week.start_date
        
        # Income transactions (bi-weekly paycheck)
        if week.week_number % 2 == 1:  # Every other week
            paycheck = Transaction(
                transaction_type=TransactionType.INCOME.value,
                week_number=week.week_number,
                amount=1200.00 + random.uniform(-100, 100),  # Paycheck variation
                date=week_start,
                description="Bi-weekly paycheck"
            )
            self.db.add(paycheck)
        
        # Spending transactions (3-8 per week)
        num_spending = random.randint(3, 8)
        for _ in range(num_spending):
            # Random day within the week
            transaction_date = week_start + timedelta(days=random.randint(0, 6))
            
            # Random amount and category
            category = random.choice(self.spending_categories)
            amount = self.generate_spending_amount(category)
            
            # 5% chance of abnormal transaction (include_in_analytics=False)
            include_in_analytics = random.random() > 0.05
            
            spending = Transaction(
                transaction_type=TransactionType.SPENDING.value,
                week_number=week.week_number,
                amount=amount,
                date=transaction_date,
                description=self.generate_spending_description(category, amount),
                category=category,
                include_in_analytics=include_in_analytics
            )
            self.db.add(spending)
            
        # Bill payments (occasional)
        if random.random() < 0.3:  # 30% chance of bill payment this week
            bill = random.choice(bills)
            bill_payment = Transaction(
                transaction_type=TransactionType.BILL_PAY.value,
                week_number=week.week_number,
                amount=bill.amount_to_pay,
                date=week_start + timedelta(days=random.randint(0, 6)),
                description=f"Paid {bill.name}",
                bill_id=bill.id,
                bill_type=bill.bill_type
            )
            self.db.add(bill_payment)
            
        # Saving transactions (occasional)
        if random.random() < 0.4:  # 40% chance of saving this week
            account = random.choice([acc for acc in accounts if not acc.is_default_save])
            saving = Transaction(
                transaction_type=TransactionType.SAVING.value,
                week_number=week.week_number,
                amount=random.uniform(50, 200),
                date=week_start + timedelta(days=random.randint(0, 6)),
                description=f"Transfer to {account.name}",
                account_id=account.id,
                account_saved_to=account.name
            )
            self.db.add(saving)
            
        self.db.commit()
        
    def generate_spending_amount(self, category):
        """Generate realistic spending amounts by category"""
        ranges = {
            "Food": (5, 50),
            "Transportation": (3, 30),
            "Entertainment": (10, 80),
            "Shopping": (15, 120),
            "Utilities": (20, 200),
            "Healthcare": (25, 150),
            "Personal Care": (5, 60),
            "Education": (10, 100),
            "Miscellaneous": (5, 75)
        }
        
        min_amt, max_amt = ranges.get(category, (5, 50))
        amount = random.uniform(min_amt, max_amt)
        
        # 5% chance of abnormal large amount
        if random.random() < 0.05:
            amount *= random.uniform(10, 50)  # Make it abnormally large
            
        return round(amount, 2)
        
    def generate_spending_description(self, category, amount):
        """Generate realistic descriptions"""
        descriptions = {
            "Food": ["Grocery store", "Restaurant", "Coffee shop", "Takeout", "Snacks"],
            "Transportation": ["Gas", "Uber", "Parking", "Bus fare", "Car wash"],
            "Entertainment": ["Movie tickets", "Streaming", "Concert", "Games", "Books"],
            "Shopping": ["Clothing", "Electronics", "Home goods", "Gifts", "Online purchase"],
            "Utilities": ["Electric bill", "Water bill", "Trash service", "Heating"],
            "Healthcare": ["Doctor visit", "Pharmacy", "Dental", "Vitamins", "Insurance"],
            "Personal Care": ["Haircut", "Toiletries", "Gym", "Beauty products"],
            "Education": ["Books", "Course fee", "Supplies", "Workshop"],
            "Miscellaneous": ["ATM fee", "Service charge", "Donation", "Other"]
        }
        
        base_desc = random.choice(descriptions.get(category, ["Purchase"]))
        
        # Add amount context for large purchases
        if amount > 500:
            base_desc = f"Large purchase: {base_desc}"
        elif amount < 5:
            base_desc = f"Small purchase: {base_desc}"
            
        return base_desc
        
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Generate sample data"""
    generator = SampleDataGenerator()
    try:
        generator.generate_all_sample_data(weeks_back=12)
        print("Sample data generation completed successfully!")
    finally:
        generator.close()


if __name__ == "__main__":
    main()