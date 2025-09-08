"""
Migration script to update bills table structure for manual payment system
"""

from sqlalchemy import text
from models import get_db


def migrate_bills_table():
    """Update bills table to support manual payment system"""
    db = get_db()
    
    try:
        print("Migrating bills table for manual payment system...")
        
        # Check existing structure
        result = db.execute(text("PRAGMA table_info(bills)"))
        columns = [row[1] for row in result.fetchall()]
        
        migrations_needed = []
        
        # Check what columns need to be added/updated
        if 'payment_frequency' not in columns:
            migrations_needed.append("ADD COLUMN payment_frequency TEXT DEFAULT 'monthly'")
        
        if 'typical_amount' not in columns:
            migrations_needed.append("ADD COLUMN typical_amount REAL DEFAULT 0.0")
            
        if 'last_payment_amount' not in columns:
            migrations_needed.append("ADD COLUMN last_payment_amount REAL DEFAULT 0.0")
            
        if 'is_variable' not in columns:
            migrations_needed.append("ADD COLUMN is_variable BOOLEAN DEFAULT 0")
            
        if 'notes' not in columns:
            migrations_needed.append("ADD COLUMN notes TEXT")
        
        # Apply migrations
        for migration in migrations_needed:
            print(f"  Applying: ALTER TABLE bills {migration}")
            db.execute(text(f"ALTER TABLE bills {migration}"))
        
        # Update existing data
        if migrations_needed:
            print("  Updating existing bill data...")
            
            # Copy amount_to_pay to typical_amount for existing bills
            if 'typical_amount' in [m.split()[-2] for m in migrations_needed]:
                db.execute(text("UPDATE bills SET typical_amount = amount_to_pay WHERE typical_amount = 0.0"))
            
            # Set payment frequencies based on days_between_payments
            if 'payment_frequency' in [m.split()[-2] for m in migrations_needed]:
                db.execute(text("""
                    UPDATE bills SET payment_frequency = 
                    CASE 
                        WHEN days_between_payments <= 10 THEN 'weekly'
                        WHEN days_between_payments <= 35 THEN 'monthly' 
                        WHEN days_between_payments <= 95 THEN 'quarterly'
                        WHEN days_between_payments <= 200 THEN 'semi-annual'
                        ELSE 'yearly'
                    END
                    WHERE payment_frequency = 'monthly'
                """))
            
            # Mark school-related bills as variable
            db.execute(text("UPDATE bills SET is_variable = 1 WHERE name LIKE '%school%' OR name LIKE '%tuition%'"))
        
        db.commit()
        
        if migrations_needed:
            print("Bills table migration completed successfully!")
            print("  - Added payment_frequency (weekly, monthly, etc.)")
            print("  - Added typical_amount for variable payments")
            print("  - Added last_payment_amount tracking")
            print("  - Added is_variable flag")
            print("  - Added notes field")
        else:
            print("Bills table already up to date!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_bills_table()