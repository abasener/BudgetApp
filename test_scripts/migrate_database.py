"""
Database migration script to add goal_amount to existing accounts
"""

from sqlalchemy import text
from models import get_db, create_tables


def migrate_database():
    """Add goal_amount column to existing accounts"""
    db = get_db()
    
    try:
        print("Checking if migration is needed...")
        
        # Check if goal_amount column already exists
        result = db.execute(text("PRAGMA table_info(accounts)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'goal_amount' in columns:
            print("✓ Database already migrated - goal_amount column exists")
            return
        
        print("Adding goal_amount column to accounts table...")
        
        # Add the goal_amount column with default value 0.0
        db.execute(text("ALTER TABLE accounts ADD COLUMN goal_amount REAL DEFAULT 0.0"))
        db.commit()
        
        # Update some existing accounts with example goals
        print("Setting example goals for some accounts...")
        
        # Set vacation fund goal
        db.execute(text("""
            UPDATE accounts 
            SET goal_amount = 2000.0 
            WHERE name = 'Vacation Fund'
        """))
        
        # Set car fund goal
        db.execute(text("""
            UPDATE accounts 
            SET goal_amount = 5000.0 
            WHERE name = 'Car Fund'
        """))
        
        db.commit()
        
        print("✓ Database migration completed successfully!")
        print("  - Added goal_amount column")
        print("  - Set example goals for Vacation Fund ($2000) and Car Fund ($5000)")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_database()