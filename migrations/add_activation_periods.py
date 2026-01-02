"""
Migration: Add activation_periods to Account and Bill tables

This migration adds support for account/bill activation periods, allowing
accounts to be active only during certain date ranges. This enables:
- Seasonal accounts (vacation savings April-August)
- Temporary goals (save for purchase, then deactivate)
- Life transitions (rent ends, mortgage starts)

The activation_periods field is a JSON list of {start, end} objects:
    [
        {"start": "2024-01-15", "end": "2024-08-31"},  # Past period
        {"start": "2025-04-01", "end": null}           # Currently active
    ]

USAGE (run from BudgetApp directory):
============================================================================

    python migrations/add_activation_periods.py

============================================================================

FOR PRODUCTION MACHINE (with real data):
============================================================================

1. BEFORE running, make sure:
   - Close the BudgetApp if it's running
   - Pull latest code from GitHub (git pull)

2. Run the migration:

   cd path/to/BudgetApp
   python migrations/add_activation_periods.py

3. Verify output shows:
   - [OK] Database backed up to: backups/budget_app_backup_YYYYMMDD_HHMMSS.db
   - [OK] Successfully added activation_periods to accounts table
   - [OK] Successfully added activation_periods to bills table
   - [OK] Initialized X accounts with activation periods
   - [OK] Initialized X bills with activation periods

4. Test the app:
   - Launch the app (python main.py)
   - Check Bills tab loads correctly
   - Check Savings tab loads correctly
   - All accounts should appear as "active" (initial state)

5. If something goes wrong, restore from backup:

   python migrations/backup_database.py restore backups/budget_app_backup_YYYYMMDD_HHMMSS.db

============================================================================

This script is IDEMPOTENT - safe to run multiple times. It will skip steps
that have already been completed.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import get_db
from sqlalchemy import text


def add_activation_periods_to_accounts():
    """Add activation_periods column to accounts table"""
    db = get_db()

    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(accounts)"))
        columns = [row[1] for row in result.fetchall()]

        if 'activation_periods' in columns:
            print("[OK] activation_periods column already exists in accounts table")
            return True

        print("Adding activation_periods column to accounts table...")

        # Add the new column (JSON stored as TEXT in SQLite)
        db.execute(text("ALTER TABLE accounts ADD COLUMN activation_periods TEXT"))
        db.commit()

        print("[OK] Successfully added activation_periods to accounts table")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to add activation_periods to accounts: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def add_activation_periods_to_bills():
    """Add activation_periods column to bills table"""
    db = get_db()

    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(bills)"))
        columns = [row[1] for row in result.fetchall()]

        if 'activation_periods' in columns:
            print("[OK] activation_periods column already exists in bills table")
            return True

        print("Adding activation_periods column to bills table...")

        # Add the new column (JSON stored as TEXT in SQLite)
        db.execute(text("ALTER TABLE bills ADD COLUMN activation_periods TEXT"))
        db.commit()

        print("[OK] Successfully added activation_periods to bills table")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to add activation_periods to bills: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def initialize_account_periods():
    """
    Initialize activation_periods for existing accounts.

    For each account without activation_periods set:
    - Use created_at date as start date (or today if created_at is NULL)
    - Set end to null (currently active)
    """
    db = get_db()

    try:
        # Get all accounts
        result = db.execute(text("""
            SELECT id, name, created_at, activation_periods
            FROM accounts
        """))
        accounts = result.fetchall()

        initialized_count = 0

        for account_id, name, created_at, existing_periods in accounts:
            # Skip if already has activation_periods
            if existing_periods:
                try:
                    periods = json.loads(existing_periods)
                    if periods:  # Non-empty list
                        continue
                except (json.JSONDecodeError, TypeError):
                    pass  # Invalid JSON, will reinitialize

            # Determine start date
            if created_at:
                # created_at might be a string or datetime
                if isinstance(created_at, str):
                    # Parse the datetime string and extract date
                    try:
                        start_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date().isoformat()
                    except ValueError:
                        start_date = created_at[:10]  # Take first 10 chars (YYYY-MM-DD)
                else:
                    start_date = created_at.date().isoformat() if hasattr(created_at, 'date') else str(created_at)[:10]
            else:
                start_date = date.today().isoformat()

            # Create initial period (currently active)
            periods = [{"start": start_date, "end": None}]
            periods_json = json.dumps(periods)

            db.execute(text("""
                UPDATE accounts
                SET activation_periods = :periods
                WHERE id = :id
            """), {"periods": periods_json, "id": account_id})

            initialized_count += 1
            print(f"   Initialized: {name} (start: {start_date})")

        db.commit()
        print(f"[OK] Initialized {initialized_count} accounts with activation periods")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to initialize account periods: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def initialize_bill_periods():
    """
    Initialize activation_periods for existing bills.
    Same logic as accounts.
    """
    db = get_db()

    try:
        # Get all bills
        result = db.execute(text("""
            SELECT id, name, created_at, activation_periods
            FROM bills
        """))
        bills = result.fetchall()

        initialized_count = 0

        for bill_id, name, created_at, existing_periods in bills:
            # Skip if already has activation_periods
            if existing_periods:
                try:
                    periods = json.loads(existing_periods)
                    if periods:  # Non-empty list
                        continue
                except (json.JSONDecodeError, TypeError):
                    pass  # Invalid JSON, will reinitialize

            # Determine start date
            if created_at:
                if isinstance(created_at, str):
                    try:
                        start_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date().isoformat()
                    except ValueError:
                        start_date = created_at[:10]
                else:
                    start_date = created_at.date().isoformat() if hasattr(created_at, 'date') else str(created_at)[:10]
            else:
                start_date = date.today().isoformat()

            # Create initial period (currently active)
            periods = [{"start": start_date, "end": None}]
            periods_json = json.dumps(periods)

            db.execute(text("""
                UPDATE bills
                SET activation_periods = :periods
                WHERE id = :id
            """), {"periods": periods_json, "id": bill_id})

            initialized_count += 1
            print(f"   Initialized: {name} (start: {start_date})")

        db.commit()
        print(f"[OK] Initialized {initialized_count} bills with activation periods")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to initialize bill periods: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def verify_migration():
    """Verify the migration completed successfully"""
    db = get_db()

    try:
        print("\nVerifying migration...")

        # Check accounts table
        result = db.execute(text("PRAGMA table_info(accounts)"))
        account_columns = [row[1] for row in result.fetchall()]

        if 'activation_periods' not in account_columns:
            print("[ERROR] activation_periods column missing from accounts table!")
            return False
        print("[OK] accounts.activation_periods column exists")

        # Check bills table
        result = db.execute(text("PRAGMA table_info(bills)"))
        bill_columns = [row[1] for row in result.fetchall()]

        if 'activation_periods' not in bill_columns:
            print("[ERROR] activation_periods column missing from bills table!")
            return False
        print("[OK] bills.activation_periods column exists")

        # Check that accounts have been initialized
        result = db.execute(text("""
            SELECT COUNT(*) FROM accounts WHERE activation_periods IS NOT NULL
        """))
        accounts_with_periods = result.fetchone()[0]

        result = db.execute(text("SELECT COUNT(*) FROM accounts"))
        total_accounts = result.fetchone()[0]

        print(f"[OK] {accounts_with_periods}/{total_accounts} accounts have activation_periods set")

        # Check that bills have been initialized
        result = db.execute(text("""
            SELECT COUNT(*) FROM bills WHERE activation_periods IS NOT NULL
        """))
        bills_with_periods = result.fetchone()[0]

        result = db.execute(text("SELECT COUNT(*) FROM bills"))
        total_bills = result.fetchone()[0]

        print(f"[OK] {bills_with_periods}/{total_bills} bills have activation_periods set")

        # Show sample data
        result = db.execute(text("""
            SELECT name, activation_periods FROM accounts LIMIT 3
        """))
        samples = result.fetchall()

        if samples:
            print("\nSample account activation_periods:")
            for name, periods in samples:
                print(f"   {name}: {periods}")

        return True

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False
    finally:
        db.close()


def run_migration():
    """Run the complete migration"""
    print("=" * 70)
    print("Migration: Add activation_periods to Account and Bill tables")
    print("=" * 70)

    # Step 1: Backup
    print("\nStep 1: Creating backup...")
    from migrations.backup_database import backup_database
    backup_path = backup_database()
    if not backup_path:
        print("[ERROR] Backup failed - aborting migration")
        print("\nNo changes were made to the database.")
        return False

    # Step 2: Add column to accounts
    print("\nStep 2: Adding activation_periods to accounts table...")
    if not add_activation_periods_to_accounts():
        print("[ERROR] Failed to modify accounts table")
        print(f"\nRestore from backup if needed: python migrations/backup_database.py restore {backup_path}")
        return False

    # Step 3: Add column to bills
    print("\nStep 3: Adding activation_periods to bills table...")
    if not add_activation_periods_to_bills():
        print("[ERROR] Failed to modify bills table")
        print(f"\nRestore from backup if needed: python migrations/backup_database.py restore {backup_path}")
        return False

    # Step 4: Initialize accounts
    print("\nStep 4: Initializing account activation periods...")
    if not initialize_account_periods():
        print("[WARN] Failed to initialize some accounts - continuing anyway")

    # Step 5: Initialize bills
    print("\nStep 5: Initializing bill activation periods...")
    if not initialize_bill_periods():
        print("[WARN] Failed to initialize some bills - continuing anyway")

    # Step 6: Verify
    print("\nStep 6: Verifying migration...")
    if not verify_migration():
        print("[WARN] Verification found issues - check output above")

    print("\n" + "=" * 70)
    print("Migration complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Launch the app and verify Bills/Savings tabs load correctly")
    print("2. All accounts should appear as active (no changes to behavior yet)")
    print(f"3. If issues occur, restore: python migrations/backup_database.py restore {backup_path}")

    return True


if __name__ == "__main__":
    run_migration()
