"""
Fix bills table schema - remove old NOT NULL constraints and unused fields
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.database import get_db
from sqlalchemy import text


def fix_bills_schema():
    """Fix the bills table schema by recreating it with correct structure"""
    db = get_db()
    
    try:
        print("Fixing bills table schema...")
        
        # Create new bills table with correct structure
        create_new_table = """
        CREATE TABLE bills_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL,
            bill_type VARCHAR NOT NULL,
            payment_frequency VARCHAR NOT NULL,
            typical_amount REAL NOT NULL DEFAULT 0.0,
            amount_to_save REAL NOT NULL DEFAULT 0.0,
            running_total REAL DEFAULT 0.0,
            last_payment_date DATE,
            last_payment_amount REAL DEFAULT 0.0,
            is_variable BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        db.execute(text(create_new_table))
        
        # Copy data from old table to new table (mapping old columns to new ones)
        copy_data = """
        INSERT INTO bills_new (
            id, name, bill_type, payment_frequency, typical_amount, amount_to_save, 
            running_total, last_payment_date, last_payment_amount, is_variable, notes, 
            created_at, updated_at
        )
        SELECT 
            id, name, bill_type, 
            COALESCE(payment_frequency, 'monthly'), 
            COALESCE(typical_amount, amount_to_pay, 0.0),
            amount_to_save, 
            COALESCE(running_total, 0.0), 
            last_payment_date, 
            COALESCE(last_payment_amount, 0.0), 
            COALESCE(is_variable, 0), 
            notes, 
            COALESCE(created_at, CURRENT_TIMESTAMP), 
            COALESCE(updated_at, CURRENT_TIMESTAMP)
        FROM bills
        """
        
        db.execute(text(copy_data))
        
        # Drop old table and rename new one
        db.execute(text("DROP TABLE bills"))
        db.execute(text("ALTER TABLE bills_new RENAME TO bills"))
        
        db.commit()
        
        print("Successfully fixed bills table schema!")
        print("- Removed old NOT NULL constraints on unused fields")
        print("- Migrated amount_to_pay to typical_amount where needed")
        print("- Clean schema matches current Bill model")
        
    except Exception as e:
        print(f"Error fixing bills schema: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    fix_bills_schema()