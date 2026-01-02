"""
Generate Test Data for BudgetApp

This script creates a fresh database with realistic test data for an entry-level IT worker.
All dates are calculated relative to the current date, with the 8th week covering today.

Usage: Run this script directly, or call from Settings dialog "Load Test Data" button.

Safety: This script drops ALL existing data and creates fresh test data.
        It only affects the local budget_app.db file in this project folder.
"""

import sys
import io

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import random
import uuid
from datetime import date, timedelta, datetime

# Database imports
from models.database import engine, Base, SessionLocal
from models.accounts import Account
from models.bills import Bill
from models.weeks import Week
from models.transactions import Transaction, TransactionType
from models.account_history import AccountHistory, AccountHistoryManager
from models.reimbursements import Reimbursement

# Service imports for proper paycheck processing
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager


def get_current_week_monday():
    """Get the Monday of the current week"""
    today = date.today()
    days_since_monday = today.weekday()  # Monday = 0
    return today - timedelta(days=days_since_monday)


def generate_test_data():
    """Generate complete test dataset with 8 weeks of data ending at current week"""

    print("=" * 60)
    print("BUDGET APP TEST DATA GENERATOR")
    print("=" * 60)

    print("\n[1/9] Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)

    print("[2/9] Creating fresh tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ================================================================
        # STEP 1: Create Savings Accounts
        # ================================================================
        print("\n[3/9] Creating savings accounts...")

        # Calculate dates for activation periods
        current_monday = get_current_week_monday()
        week1_start = current_monday - timedelta(weeks=7)
        data_start_date = week1_start - timedelta(days=1)

        # Active since start of data - standard active account
        active_since_start = [{"start": data_start_date.isoformat(), "end": None}]

        # Inactive account - was active but ended 2 weeks ago (Steam Sale Fund)
        steam_sale_end = current_monday - timedelta(weeks=2)
        steam_sale_start = data_start_date
        inactive_seasonal = [{"start": steam_sale_start.isoformat(), "end": steam_sale_end.isoformat()}]

        # Reactivated account - was inactive, now active again (Conventions Fund)
        # First period: data start to 4 weeks ago (deactivated)
        # Second period: 1 week ago to now (reactivated)
        conventions_first_end = current_monday - timedelta(weeks=4)
        conventions_second_start = current_monday - timedelta(weeks=1)
        reactivated_periods = [
            {"start": data_start_date.isoformat(), "end": conventions_first_end.isoformat()},
            {"start": conventions_second_start.isoformat(), "end": None}
        ]

        # Helper to convert date to datetime for created_at
        def date_to_datetime(d):
            return datetime.combine(d, datetime.min.time())

        accounts = [
            Account(
                name="Safety Saving",  # Matches Scratch Pad example
                goal_amount=5000.00,
                auto_save_amount=50.00,
                is_default_save=True,  # Rollovers go here
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Account(
                name="Vacation",
                goal_amount=2000.00,
                auto_save_amount=25.00,
                is_default_save=False,
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Account(
                name="New Home",
                goal_amount=20000.00,
                auto_save_amount=100.00,
                is_default_save=False,
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Account(
                name="Steam Sale Fund",  # Seasonal - for Summer/Winter sales
                goal_amount=200.00,
                auto_save_amount=15.00,
                is_default_save=False,
                activation_periods=inactive_seasonal,  # Currently INACTIVE
                created_at=date_to_datetime(steam_sale_start)
            ),
            Account(
                name="Conventions Fund",  # Was inactive, now reactivated for upcoming con
                goal_amount=500.00,
                auto_save_amount=30.00,
                is_default_save=False,
                activation_periods=reactivated_periods,  # Gap in middle, now active
                created_at=date_to_datetime(data_start_date)
            ),
        ]

        for account in accounts:
            db.add(account)
        db.commit()

        # Refresh to get IDs
        for account in accounts:
            db.refresh(account)

        print(f"   Created {len(accounts)} accounts:")
        for a in accounts:
            status = "ACTIVE" if a.is_currently_active else "INACTIVE"
            print(f"      {a.name}: {status} - {a.get_display_date_range()}")

        # ================================================================
        # STEP 2: Create Bills
        # ================================================================
        print("\n[4/9] Creating bills...")

        # Inactive bill - cancelled gym membership (ended 3 weeks ago)
        gym_end = current_monday - timedelta(weeks=3)
        inactive_gym = [{"start": data_start_date.isoformat(), "end": gym_end.isoformat()}]

        # Recently activated bill - new streaming bundle (started 2 weeks ago)
        streaming_start = current_monday - timedelta(weeks=2)
        new_streaming = [{"start": streaming_start.isoformat(), "end": None}]

        bills = [
            Bill(
                name="Rent",  # Matches Scratch Pad example
                bill_type="Housing",
                payment_frequency="monthly",
                typical_amount=1200.00,
                amount_to_save=600.00,  # Per paycheck (bi-weekly)
                is_variable=False,
                notes="Due on the 1st",
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Bill(
                name="Insurance",
                bill_type="Insurance",
                payment_frequency="monthly",
                typical_amount=150.00,
                amount_to_save=75.00,
                is_variable=False,
                notes="Auto insurance",
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Bill(
                name="Internet",
                bill_type="Utilities",
                payment_frequency="monthly",
                typical_amount=80.00,
                amount_to_save=40.00,
                is_variable=False,
                notes="Fiber connection for remote work",
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Bill(
                name="Taxes",
                bill_type="Taxes",
                payment_frequency="yearly",
                typical_amount=500.00,
                amount_to_save=25.00,  # Small amount per paycheck
                is_variable=True,
                notes="Estimated quarterly + year-end",
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Bill(
                name="Phone",
                bill_type="Utilities",
                payment_frequency="monthly",
                typical_amount=45.00,
                amount_to_save=22.50,
                is_variable=False,
                notes="Mobile plan",
                activation_periods=active_since_start,
                created_at=date_to_datetime(data_start_date)
            ),
            Bill(
                name="Gym Membership",  # INACTIVE - cancelled to save money
                bill_type="Health",
                payment_frequency="monthly",
                typical_amount=35.00,
                amount_to_save=17.50,
                is_variable=False,
                notes="Planet Fitness - cancelled, doing home workouts instead",
                activation_periods=inactive_gym,  # Currently INACTIVE
                created_at=date_to_datetime(data_start_date)
            ),
            Bill(
                name="Streaming Bundle",  # NEW - just started
                bill_type="Entertainment",
                payment_frequency="monthly",
                typical_amount=25.00,
                amount_to_save=12.50,
                is_variable=False,
                notes="Disney+, Hulu, ESPN combo - because Marvel",
                activation_periods=new_streaming,  # Recently activated
                created_at=date_to_datetime(streaming_start)
            ),
        ]

        for bill in bills:
            db.add(bill)
        db.commit()

        for bill in bills:
            db.refresh(bill)

        print(f"   Created {len(bills)} bills:")
        for b in bills:
            status = "ACTIVE" if b.is_currently_active else "INACTIVE"
            print(f"      {b.name}: {status} - {b.get_display_date_range()}")

        # ================================================================
        # STEP 3: Initialize Account History (Starting Balances)
        # ================================================================
        print("\n[5/9] Initializing account history...")

        history_manager = AccountHistoryManager(db)

        # Set starting balances for accounts
        account_starting_balances = {
            "Safety Saving": 500.00,   # Some existing savings
            "Vacation": 150.00,
            "New Home": 1000.00,
            "Steam Sale Fund": 85.00,  # Had some saved before deactivating
            "Conventions Fund": 120.00,  # From previous convention savings
        }

        for account in accounts:
            starting_balance = account_starting_balances.get(account.name, 0.0)
            history_manager.initialize_account_history(
                account_id=account.id,
                account_type="savings",
                starting_balance=starting_balance,
                start_date=data_start_date
            )
            print(f"   {account.name}: Starting balance ${starting_balance:.2f}")

        # Set starting balances for bills (some already have partial savings)
        bill_starting_balances = {
            "Rent": 400.00,      # Partial from last month
            "Insurance": 50.00,
            "Internet": 20.00,
            "Taxes": 75.00,
            "Phone": 10.00,
            "Gym Membership": 35.00,  # Had one payment saved before cancelling
            "Streaming Bundle": 0.00,  # New, no history yet
        }

        for bill in bills:
            starting_balance = bill_starting_balances.get(bill.name, 0.0)
            history_manager.initialize_account_history(
                account_id=bill.id,
                account_type="bill",
                starting_balance=starting_balance,
                start_date=data_start_date
            )
            print(f"   {bill.name}: Starting balance ${starting_balance:.2f}")

        db.commit()

        # ================================================================
        # STEP 4: Process Paychecks (creates weeks automatically)
        # ================================================================
        print("\n[6/9] Processing paychecks...")

        paycheck_processor = PaycheckProcessor()

        # Entry-level IT salary: ~$50-55k/year = ~$1,900-$2,100 net per paycheck
        base_paycheck = 2050.00
        paycheck_amounts = [
            base_paycheck + random.uniform(-100, 150),  # Pay period 1
            base_paycheck + random.uniform(-50, 200),   # Pay period 2
            base_paycheck + random.uniform(-100, 100),  # Pay period 3
            base_paycheck + random.uniform(-75, 175),   # Pay period 4
        ]

        for i, amount in enumerate(paycheck_amounts):
            # Calculate dates for this pay period
            period_week1_start = week1_start + timedelta(weeks=i * 2)
            pay_date = period_week1_start + timedelta(days=4)  # Friday of week 1

            print(f"   Paycheck {i+1}: ${amount:.2f} on {pay_date} (week starting {period_week1_start})")

            # Use paycheck processor - it handles everything including weeks creation
            paycheck_processor.process_new_paycheck(
                paycheck_amount=round(amount, 2),
                paycheck_date=pay_date,
                week_start_date=period_week1_start
            )

        # ================================================================
        # STEP 5: Pay Some Bills
        # ================================================================
        print("\n[7/9] Paying bills...")

        transaction_manager = TransactionManager()

        # Get weeks from database
        weeks = db.query(Week).order_by(Week.week_number).all()
        today = date.today()
        yesterday = today - timedelta(days=1)

        def pay_bill(bill, week_idx, day_offset=0):
            """Helper to pay a bill if the date is valid"""
            if week_idx >= len(weeks):
                return False
            pay_date = weeks[week_idx].start_date + timedelta(days=day_offset)
            if pay_date > yesterday:
                return False

            # Create bill_pay transaction (same pattern as PayBillDialog)
            transaction_data = {
                "transaction_type": "bill_pay",
                "amount": bill.typical_amount,
                "date": pay_date,
                "description": f"Paid {bill.name}",
                "week_number": weeks[week_idx].week_number,
                "bill_id": bill.id,
                "category": f"Bill Payment - {bill.bill_type}"
            }
            transaction_manager.add_transaction(transaction_data)

            # Update bill payment tracking
            bill.last_payment_date = pay_date
            bill.last_payment_amount = bill.typical_amount
            db.commit()

            print(f"   Paid {bill.name}: ${bill.typical_amount:.2f} on {pay_date}")
            return True

        # Rent - paid once in week 2 and week 6
        rent_bill = next(b for b in bills if b.name == "Rent")
        pay_bill(rent_bill, 1, random.randint(0, 2))  # Week 2
        pay_bill(rent_bill, 5, random.randint(0, 2))  # Week 6

        # Internet - paid in week 3
        internet_bill = next(b for b in bills if b.name == "Internet")
        pay_bill(internet_bill, 2, 1)

        # Phone - paid in week 4
        phone_bill = next(b for b in bills if b.name == "Phone")
        pay_bill(phone_bill, 3, 2)

        # Insurance - paid in week 5
        insurance_bill = next(b for b in bills if b.name == "Insurance")
        pay_bill(insurance_bill, 4, 3)

        db.commit()

        # ================================================================
        # STEP 6: Create Spending Transactions (The Fun Part!)
        # ================================================================
        print("\n[8/9] Creating spending transactions...")

        # Easter egg spending descriptions by category
        spending_templates = {
            "Food": [
                # Normal ones
                ("Groceries at Trader Joe's", 45.00, 75.00),
                ("Lunch at work", 8.00, 15.00),
                ("Coffee run", 4.50, 7.00),
                ("Takeout dinner", 15.00, 25.00),
                ("Weekly groceries", 50.00, 90.00),
                # Nerdy ones
                ("Lembas bread from the Elves", 12.00, 18.00),
                ("Second breakfast at the Prancing Pony", 14.00, 22.00),
                ("Butterbeer at Three Broomsticks", 6.00, 9.00),
                ("Blue milk at Mos Eisley Cantina", 5.00, 8.00),
                ("Pizza at Michelangelo's request", 18.00, 28.00),
                ("Tubby Custard from the kitchen", 3.00, 5.00),
                ("Fish fingers and custard", 7.00, 12.00),
                ("Senzu beans from Korin", 15.00, 20.00),
                ("Tea with Iroh", 4.00, 6.00),
            ],
            "Gas": [
                # Normal ones
                ("Gas station fill-up", 35.00, 50.00),
                ("Weekly gas", 38.00, 48.00),
                # Nerdy ones
                ("Plutonium for the DeLorean", 42.00, 52.00),
                ("Dilithium crystals from SpaceDock", 44.00, 55.00),
                ("Fuel for the Millennium Falcon", 40.00, 50.00),
                ("Energon for Bumblebee", 38.00, 47.00),
            ],
            "Entertainment": [
                # Normal ones
                ("Movie tickets", 12.00, 18.00),
                ("Streaming subscription", 15.00, 20.00),
                ("Video game", 25.00, 65.00),
                ("Concert tickets", 45.00, 80.00),
                # Nerdy ones
                ("Holodeck time on the Enterprise", 20.00, 35.00),
                ("Quidditch World Cup tickets", 55.00, 75.00),
                ("Tickets to see the Cantina Band", 25.00, 40.00),
                ("VIP pass to Comic-Con", 60.00, 90.00),
                ("New dice set for D&D night", 15.00, 30.00),
                ("Bought a painting from Data", 35.00, 55.00),
                ("Holonovel: Adventures of Captain Proton", 12.00, 18.00),
                ("Sabacc game at Cloud City", 20.00, 45.00),
                ("Poetry night at Vogon open mic", 8.00, 15.00),
                ("Watched fireworks from Bag End", 10.00, 20.00),
                # Steam/Gaming references
                ("Steam wishlist impulse buy", 15.00, 40.00),
                ("Indie game from itch.io", 5.00, 15.00),
                ("Cosmetics in Destiny 2", 10.00, 20.00),
                ("MTG Arena wildcards", 20.00, 50.00),
                ("New mount in WoW", 15.00, 25.00),
            ],
            "Misc": [
                # Normal ones
                ("Household supplies", 15.00, 35.00),
                ("Pharmacy run", 10.00, 25.00),
                ("Pet supplies", 20.00, 40.00),
                ("Clothing", 25.00, 60.00),
                ("Haircut", 18.00, 30.00),
                # Nerdy ones
                ("Sonic screwdriver batteries", 12.00, 20.00),
                ("New towel from the Guide", 22.00, 35.00),
                ("Replaced the flux capacitor", 45.00, 70.00),
                ("Reparo supplies from Diagon Alley", 18.00, 28.00),
                ("Starfleet uniform dry cleaning", 15.00, 25.00),
                ("Fed the Mogwai after midnight oops", 30.00, 50.00),
                ("Lightsaber crystal polishing kit", 25.00, 40.00),
                ("Replaced my towel again", 22.00, 35.00),
            ],
            "Transport": [
                # Normal ones
                ("Uber ride", 12.00, 25.00),
                ("Parking", 5.00, 15.00),
                ("Bus pass", 25.00, 40.00),
                # Nerdy ones
                ("Floo powder restock", 8.00, 15.00),
                ("Portkey registration fee", 20.00, 30.00),
                ("Speeder bike maintenance", 35.00, 55.00),
                ("TARDIS parking fine", 10.00, 20.00),
            ],
            "Health": [
                # Normal ones
                ("Gym membership", 30.00, 45.00),
                ("Vitamins", 15.00, 25.00),
                # Nerdy ones
                ("Bacta tank session", 40.00, 60.00),
                ("Potion from the Hospital Wing", 15.00, 25.00),
                ("Meditation with Master Yoda", 20.00, 35.00),
            ],
        }

        # Weight categories - needs vs wants (Food/Gas more frequent than Entertainment)
        category_weights = {
            "Food": 0.35,
            "Gas": 0.15,
            "Entertainment": 0.15,
            "Misc": 0.15,
            "Transport": 0.10,
            "Health": 0.10,
        }

        total_spending_count = 0

        # Reload weeks to get updated data
        weeks = db.query(Week).order_by(Week.week_number).all()

        for week in weeks:
            # Determine how many transactions this week (4-8 per week)
            num_transactions = random.randint(4, 8)

            # Calculate valid date range for this week
            week_end = min(week.end_date, yesterday)  # Don't go past yesterday

            if week.start_date > yesterday:
                # This week hasn't started yet (future) - skip spending
                print(f"   Week {week.week_number}: Skipping (future week)")
                continue

            print(f"   Week {week.week_number}: Adding {num_transactions} transactions")

            for _ in range(num_transactions):
                # Pick a category based on weights
                category = random.choices(
                    list(category_weights.keys()),
                    weights=list(category_weights.values())
                )[0]

                # Pick a random transaction from that category
                template = random.choice(spending_templates[category])
                description = template[0]
                amount = round(random.uniform(template[1], template[2]), 2)

                # Pick a random date within the valid range
                days_in_range = (week_end - week.start_date).days
                if days_in_range < 0:
                    continue
                transaction_date = week.start_date + timedelta(days=random.randint(0, max(0, days_in_range)))

                # Ensure we don't add transactions in the future
                if transaction_date > yesterday:
                    transaction_date = yesterday

                # Create the transaction (use .value for enum to store as string)
                transaction = Transaction(
                    transaction_type=TransactionType.SPENDING.value,
                    amount=amount,
                    date=transaction_date,
                    description=description,
                    category=category,
                    week_number=week.week_number,
                    include_in_analytics=True
                )
                db.add(transaction)
                total_spending_count += 1

        db.commit()
        print(f"\n   Created {total_spending_count} spending transactions total")

        # ================================================================
        # STEP 6b: Create ABNORMAL Spending Transactions (for testing checkbox)
        # ================================================================
        print("\n   Adding abnormal spending transactions...")

        abnormal_transactions = [
            # One-time unusual purchases that shouldn't affect analytics
            ("Emergency car repair - one time", 450.00, "Misc", 2),
            ("Medical expense - wisdom teeth", 350.00, "Health", 3),
            ("Replaced laptop after accident", 800.00, "Misc", 4),
            ("Wedding gift for friend", 150.00, "Misc", 5),
            ("Bought a real lightsaber replica", 275.00, "Entertainment", 6),
        ]

        abnormal_count = 0
        for desc, amount, category, week_idx in abnormal_transactions:
            if week_idx < len(weeks):
                week = weeks[week_idx]
                trans_date = week.start_date + timedelta(days=random.randint(1, 4))
                if trans_date <= yesterday:
                    transaction = Transaction(
                        transaction_type=TransactionType.SPENDING.value,
                        amount=amount,
                        date=trans_date,
                        description=desc,
                        category=category,
                        week_number=week.week_number,
                        include_in_analytics=False  # ABNORMAL - excluded from analytics
                    )
                    db.add(transaction)
                    abnormal_count += 1
                    print(f"      [ABNORMAL] {desc}: ${amount:.2f}")

        db.commit()
        print(f"   Created {abnormal_count} abnormal spending transactions")

        # ================================================================
        # STEP 7: Add a Few Reimbursements for Testing
        # ================================================================
        print("\n[9/9] Creating reimbursements...")

        reimbursements_created = 0
        if len(weeks) > 2:
            reimbursement_data = [
                {
                    "amount": 125.00,
                    "date": weeks[1].start_date + timedelta(days=2),
                    "state": "reimbursed",
                    "notes": "Conference parking",
                    "category": "Transport",
                    "location": "TechConf2024",
                    "submitted_date": weeks[1].start_date + timedelta(days=3),
                    "reimbursed_date": weeks[2].start_date + timedelta(days=1) if len(weeks) > 2 else None,
                },
            ]
            if len(weeks) > 3:
                reimbursement_data.append({
                    "amount": 89.50,
                    "date": weeks[3].start_date + timedelta(days=1),
                    "state": "submitted",
                    "notes": "Team lunch",
                    "category": "Food",
                    "location": "OffSite",
                    "submitted_date": weeks[3].start_date + timedelta(days=4),
                })
            if len(weeks) > 5:
                reimbursement_data.append({
                    "amount": 45.00,
                    "date": weeks[5].start_date,
                    "state": "pending",
                    "notes": "Office supplies",
                    "category": "Supplies",
                    "location": "HomeOffice",
                })

            for r_data in reimbursement_data:
                if r_data["date"] <= yesterday:
                    r = Reimbursement(**r_data)
                    db.add(r)
                    reimbursements_created += 1

            db.commit()

        print(f"   Created {reimbursements_created} reimbursements")

        # ================================================================
        # STEP 8: Create Transfer Transactions (for testing Transfers tab)
        # ================================================================
        print("\n[10/10] Creating transfer transactions...")

        transfer_count = 0

        # Get account/bill references
        safety_account = next(a for a in accounts if a.name == "Safety Saving")
        vacation_account = next(a for a in accounts if a.name == "Vacation")
        new_home_account = next(a for a in accounts if a.name == "New Home")
        rent_bill = next(b for b in bills if b.name == "Rent")

        # --- WEEK -> ACCOUNT TRANSFERS (positive amount) ---
        # User moves money from week spending to savings
        if len(weeks) > 2:
            trans_date = weeks[2].start_date + timedelta(days=3)
            if trans_date <= yesterday:
                # Week 3 -> Safety Saving: $50
                transfer = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=50.00,  # Positive = into account
                    date=trans_date,
                    description="Moving extra to safety net",
                    week_number=weeks[2].week_number,
                    account_id=safety_account.id,
                    category="Transfer"
                )
                db.add(transfer)
                db.flush()  # Get the transaction ID
                # Record in account history
                history_manager.add_transaction_change(
                    account_id=safety_account.id,
                    account_type="savings",
                    change_amount=50.00,
                    transaction_date=trans_date,
                    transaction_id=transfer.id
                )
                transfer_count += 1
                print(f"   Week {weeks[2].week_number} -> Safety Saving: $50.00")

        if len(weeks) > 4:
            trans_date = weeks[4].start_date + timedelta(days=2)
            if trans_date <= yesterday:
                # Week 5 -> Vacation: $100
                transfer = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=100.00,  # Positive = into account
                    date=trans_date,
                    description="Vacation fund boost",
                    week_number=weeks[4].week_number,
                    account_id=vacation_account.id,
                    category="Transfer"
                )
                db.add(transfer)
                db.flush()
                history_manager.add_transaction_change(
                    account_id=vacation_account.id,
                    account_type="savings",
                    change_amount=100.00,
                    transaction_date=trans_date,
                    transaction_id=transfer.id
                )
                transfer_count += 1
                print(f"   Week {weeks[4].week_number} -> Vacation: $100.00")

        # --- ACCOUNT -> WEEK TRANSFERS (negative amount) ---
        # User pulls money from savings back to week for spending
        if len(weeks) > 5:
            trans_date = weeks[5].start_date + timedelta(days=1)
            if trans_date <= yesterday:
                # Vacation -> Week 6: $25 (withdrawing some vacation fund)
                transfer = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=-25.00,  # Negative = out of account
                    date=trans_date,
                    description="Need extra for week expenses",
                    week_number=weeks[5].week_number,
                    account_id=vacation_account.id,
                    category="Transfer"
                )
                db.add(transfer)
                db.flush()
                history_manager.add_transaction_change(
                    account_id=vacation_account.id,
                    account_type="savings",
                    change_amount=-25.00,
                    transaction_date=trans_date,
                    transaction_id=transfer.id
                )
                transfer_count += 1
                print(f"   Vacation -> Week {weeks[5].week_number}: $25.00")

        # --- WEEK -> BILL TRANSFERS ---
        # User adds extra to a bill fund
        if len(weeks) > 3:
            trans_date = weeks[3].start_date + timedelta(days=4)
            if trans_date <= yesterday:
                # Week 4 -> Rent: $75 (extra toward rent)
                transfer = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=75.00,  # Positive = into bill account
                    date=trans_date,
                    description="Extra for rent cushion",
                    week_number=weeks[3].week_number,
                    bill_id=rent_bill.id,
                    category="Transfer"
                )
                db.add(transfer)
                db.flush()
                history_manager.add_transaction_change(
                    account_id=rent_bill.id,
                    account_type="bill",
                    change_amount=75.00,
                    transaction_date=trans_date,
                    transaction_id=transfer.id
                )
                transfer_count += 1
                print(f"   Week {weeks[3].week_number} -> Rent: $75.00")

        # --- ACCOUNT -> ACCOUNT TRANSFERS (two linked transactions) ---
        # Moving money between savings accounts - uses transfer_group_id to link pair
        if len(weeks) > 6:
            trans_date = weeks[6].start_date + timedelta(days=2)
            if trans_date <= yesterday:
                # Safety Saving -> New Home: $200
                # Generate a group ID to link both transactions
                group_id = str(uuid.uuid4())

                # Transaction 1: Withdrawal from Safety Saving (negative)
                transfer_out = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=-200.00,  # Negative = out of source
                    date=trans_date,
                    description="Transfer to New Home fund",
                    week_number=weeks[6].week_number,
                    account_id=safety_account.id,
                    category="Transfer",
                    transfer_group_id=group_id  # Link to partner transaction
                )
                db.add(transfer_out)
                db.flush()
                history_manager.add_transaction_change(
                    account_id=safety_account.id,
                    account_type="savings",
                    change_amount=-200.00,
                    transaction_date=trans_date,
                    transaction_id=transfer_out.id
                )

                # Transaction 2: Deposit to New Home (positive)
                transfer_in = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=200.00,  # Positive = into destination
                    date=trans_date,
                    description="Transfer from Safety Saving",
                    week_number=weeks[6].week_number,
                    account_id=new_home_account.id,
                    category="Transfer",
                    transfer_group_id=group_id  # Same group ID links the pair
                )
                db.add(transfer_in)
                db.flush()
                history_manager.add_transaction_change(
                    account_id=new_home_account.id,
                    account_type="savings",
                    change_amount=200.00,
                    transaction_date=trans_date,
                    transaction_id=transfer_in.id
                )

                transfer_count += 2  # Two transactions for account-to-account
                print(f"   Safety Saving -> New Home: $200.00 (linked pair: {group_id[:8]}...)")

        # Second Account -> Account transfer for more test coverage
        if len(weeks) > 4:
            trans_date = weeks[4].start_date + timedelta(days=5)
            if trans_date <= yesterday:
                # Vacation -> Safety Saving: $75
                group_id2 = str(uuid.uuid4())

                # Transaction 1: Withdrawal from Vacation (negative)
                transfer_out2 = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=-75.00,
                    date=trans_date,
                    description="Reallocating to safety fund",
                    week_number=weeks[4].week_number,
                    account_id=vacation_account.id,
                    category="Transfer",
                    transfer_group_id=group_id2
                )
                db.add(transfer_out2)
                db.flush()
                history_manager.add_transaction_change(
                    account_id=vacation_account.id,
                    account_type="savings",
                    change_amount=-75.00,
                    transaction_date=trans_date,
                    transaction_id=transfer_out2.id
                )

                # Transaction 2: Deposit to Safety Saving (positive)
                transfer_in2 = Transaction(
                    transaction_type=TransactionType.SAVING.value,
                    amount=75.00,
                    date=trans_date,
                    description="Received from Vacation fund",
                    week_number=weeks[4].week_number,
                    account_id=safety_account.id,
                    category="Transfer",
                    transfer_group_id=group_id2
                )
                db.add(transfer_in2)
                db.flush()
                history_manager.add_transaction_change(
                    account_id=safety_account.id,
                    account_type="savings",
                    change_amount=75.00,
                    transaction_date=trans_date,
                    transaction_id=transfer_in2.id
                )

                transfer_count += 2
                print(f"   Vacation -> Safety Saving: $75.00 (linked pair: {group_id2[:8]}...)")

        db.commit()
        print(f"   Created {transfer_count} transfer transactions")

        # ================================================================
        # Trigger final rollover recalculations
        # ================================================================
        print("\nRecalculating rollovers...")
        for i in range(0, len(weeks), 2):
            if i < len(weeks):
                paycheck_processor.recalculate_period_rollovers(weeks[i].week_number)
        db.commit()

        # ================================================================
        # SUMMARY
        # ================================================================
        print("\n" + "=" * 60)
        print("TEST DATA GENERATION COMPLETE!")
        print("=" * 60)

        # Show final balances
        print("\nFinal Account Balances:")
        for account in accounts:
            db.refresh(account)
            balance = history_manager.get_current_balance(account.id, "savings")
            print(f"   {account.name}: ${balance:.2f}")

        print("\nFinal Bill Balances:")
        for bill in bills:
            db.refresh(bill)
            balance = history_manager.get_current_balance(bill.id, "bill")
            print(f"   {bill.name}: ${balance:.2f}")

        print("\nWeek Summary:")
        weeks = db.query(Week).order_by(Week.week_number).all()
        for week in weeks:
            db.refresh(week)
            spending = db.query(Transaction).filter(
                Transaction.week_number == week.week_number,
                Transaction.transaction_type == TransactionType.SPENDING.value
            ).count()
            is_current = week.start_date <= today <= week.end_date
            marker = " <-- CURRENT" if is_current else ""
            print(f"   Week {week.week_number} ({week.start_date}): "
                  f"${week.running_total:.2f} base, {spending} spending{marker}")

        # Summary counts
        total_abnormal = db.query(Transaction).filter(
            Transaction.transaction_type == TransactionType.SPENDING.value,
            Transaction.include_in_analytics == False
        ).count()
        total_transfers = db.query(Transaction).filter(
            Transaction.transaction_type == TransactionType.SAVING.value
        ).count()
        linked_transfers = db.query(Transaction).filter(
            Transaction.transfer_group_id != None
        ).count()

        print(f"\nTransaction Counts:")
        print(f"   Normal spending: {total_spending_count}")
        print(f"   Abnormal spending (excluded from analytics): {total_abnormal}")
        print(f"   Transfers (type=saving): {total_transfers}")
        print(f"   Linked transfer pairs: {linked_transfers // 2} pairs ({linked_transfers} transactions)")

        print("\nReady to test! Run main.py to see the app with test data.")

    except Exception as e:
        db.rollback()
        print(f"\nError generating test data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()
        paycheck_processor.close()
        transaction_manager.close()


if __name__ == "__main__":
    generate_test_data()
