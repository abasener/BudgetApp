"""
Migration to add transfer_group_id field to transactions table

This field links paired Account-to-Account transfer transactions.
When money is transferred from Account A to Account B, two transactions are created:
  1. Withdrawal from Account A (negative amount)
  2. Deposit to Account B (positive amount)

Both transactions share the same transfer_group_id to maintain their relationship.

For Week-to-Account or Account-to-Week transfers (single transaction),
transfer_group_id is NULL.

USAGE:
    python migrations/add_transfer_group_id.py

This script is idempotent - safe to run multiple times.
"""

import sys
import uuid
from pathlib import Path
from datetime import timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.database import get_db
from sqlalchemy import text


def add_transfer_group_id_field():
    """Add transfer_group_id field to transactions table"""
    db = get_db()

    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(transactions)"))
        columns = [row[1] for row in result.fetchall()]

        if 'transfer_group_id' not in columns:
            print("Adding transfer_group_id field to transactions table...")

            # Add the new column (nullable, no default)
            db.execute(text("ALTER TABLE transactions ADD COLUMN transfer_group_id VARCHAR(36)"))
            db.commit()

            print("[OK] Successfully added transfer_group_id field")
        else:
            print("[OK] transfer_group_id field already exists")

        return True

    except Exception as e:
        print(f"[ERROR] Error adding transfer_group_id field: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def link_existing_transfer_pairs():
    """
    Find existing Account-to-Account transfer pairs and link them.

    Detection criteria for a pair:
    - Both transactions have type='saving'
    - Both have account_id set (not bill_id)
    - Same date
    - Same absolute amount
    - Opposite signs (one positive, one negative)
    - Different account_ids

    This is conservative - we only link transactions that clearly match.
    """
    db = get_db()

    try:
        print("\nScanning for existing Account-to-Account transfer pairs...")

        # Get all saving transactions with account_id (not bill)
        result = db.execute(text("""
            SELECT id, transaction_type, amount, date, account_id, bill_id,
                   week_number, description, transfer_group_id
            FROM transactions
            WHERE transaction_type = 'saving'
              AND account_id IS NOT NULL
              AND bill_id IS NULL
            ORDER BY date, id
        """))

        transactions = result.fetchall()
        print(f"   Found {len(transactions)} saving transactions with account_id")

        # Group by date for efficient pair detection
        by_date = {}
        for row in transactions:
            trans_id, trans_type, amount, date, account_id, bill_id, week_num, desc, group_id = row
            if date not in by_date:
                by_date[date] = []
            by_date[date].append({
                'id': trans_id,
                'amount': amount,
                'account_id': account_id,
                'week_number': week_num,
                'description': desc or '',
                'transfer_group_id': group_id
            })

        pairs_found = 0
        pairs_linked = 0

        # Find pairs on each date
        for date, trans_list in by_date.items():
            # Skip if only one transaction on this date
            if len(trans_list) < 2:
                continue

            # Check each pair
            for i, t1 in enumerate(trans_list):
                for t2 in trans_list[i + 1:]:
                    # Check if this is a pair:
                    # 1. Opposite signs
                    # 2. Same absolute amount
                    # 3. Different accounts
                    if (t1['amount'] * t2['amount'] < 0 and  # Opposite signs
                            abs(abs(t1['amount']) - abs(t2['amount'])) < 0.01 and  # Same amount
                            t1['account_id'] != t2['account_id']):  # Different accounts

                        pairs_found += 1

                        # Check if already linked
                        if t1['transfer_group_id'] and t2['transfer_group_id']:
                            if t1['transfer_group_id'] == t2['transfer_group_id']:
                                print(f"   [SKIP] Already linked: IDs {t1['id']} <-> {t2['id']}")
                            else:
                                print(f"   [WARN] Different group IDs: {t1['id']} ({t1['transfer_group_id']}) vs {t2['id']} ({t2['transfer_group_id']})")
                            continue

                        # Generate new group ID and link them
                        group_id = str(uuid.uuid4())

                        db.execute(text("""
                            UPDATE transactions
                            SET transfer_group_id = :group_id
                            WHERE id IN (:id1, :id2)
                        """), {'group_id': group_id, 'id1': t1['id'], 'id2': t2['id']})

                        pairs_linked += 1
                        neg_trans = t1 if t1['amount'] < 0 else t2
                        pos_trans = t2 if t1['amount'] < 0 else t1
                        print(f"   [LINKED] IDs {neg_trans['id']} <-> {pos_trans['id']}: "
                              f"${abs(t1['amount']):.2f} (group: {group_id[:8]}...)")

        db.commit()

        print(f"\n   Pairs found: {pairs_found}")
        print(f"   Pairs linked: {pairs_linked}")

        return True

    except Exception as e:
        print(f"[ERROR] Error linking transfer pairs: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def verify_migration():
    """Verify the migration was successful"""
    db = get_db()

    try:
        print("\nVerifying migration...")

        # Check column exists
        result = db.execute(text("PRAGMA table_info(transactions)"))
        columns = [row[1] for row in result.fetchall()]

        if 'transfer_group_id' not in columns:
            print("[ERROR] transfer_group_id column not found!")
            return False

        print("[OK] transfer_group_id column exists")

        # Count transactions with group IDs
        result = db.execute(text("""
            SELECT COUNT(*) FROM transactions WHERE transfer_group_id IS NOT NULL
        """))
        linked_count = result.fetchone()[0]

        result = db.execute(text("""
            SELECT COUNT(DISTINCT transfer_group_id) FROM transactions
            WHERE transfer_group_id IS NOT NULL
        """))
        group_count = result.fetchone()[0]

        print(f"[OK] {linked_count} transactions linked in {group_count} groups")

        # Show sample of linked pairs
        if group_count > 0:
            result = db.execute(text("""
                SELECT t1.id, t1.amount, t1.account_id, t2.id, t2.amount, t2.account_id
                FROM transactions t1
                JOIN transactions t2 ON t1.transfer_group_id = t2.transfer_group_id AND t1.id < t2.id
                LIMIT 3
            """))
            samples = result.fetchall()

            if samples:
                print("\n   Sample linked pairs:")
                for row in samples:
                    print(f"     ID {row[0]} (${row[1]:.2f}, acct {row[2]}) <-> "
                          f"ID {row[3]} (${row[4]:.2f}, acct {row[5]})")

        return True

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False
    finally:
        db.close()


def run_migration():
    """Run the complete migration"""
    print("=" * 60)
    print("Migration: Add transfer_group_id to transactions table")
    print("=" * 60)

    # Step 1: Backup first
    print("\nStep 1: Creating backup...")
    from migrations.backup_database import backup_database
    backup_path = backup_database()
    if not backup_path:
        print("[ERROR] Backup failed - aborting migration")
        return False

    # Step 2: Add column
    print("\nStep 2: Adding transfer_group_id column...")
    if not add_transfer_group_id_field():
        print("[ERROR] Failed to add column - check backup to restore")
        return False

    # Step 3: Link existing pairs
    print("\nStep 3: Linking existing transfer pairs...")
    if not link_existing_transfer_pairs():
        print("[WARN] Failed to link pairs - column was added but pairs not linked")
        # Don't fail here - column was added successfully

    # Step 4: Verify
    print("\nStep 4: Verifying migration...")
    verify_migration()

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    run_migration()
