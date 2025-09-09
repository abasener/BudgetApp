"""
Migration to add auto_save_amount field to accounts table
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.database import get_db
from sqlalchemy import text


def add_auto_save_amount_field():
    """Add auto_save_amount field to accounts table"""
    db = get_db()
    
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(accounts)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'auto_save_amount' not in columns:
            print("Adding auto_save_amount field to accounts table...")
            
            # Add the new column with default value 0.0
            db.execute(text("ALTER TABLE accounts ADD COLUMN auto_save_amount REAL DEFAULT 0.0"))
            db.commit()
            
            print("Successfully added auto_save_amount field")
        else:
            print("auto_save_amount field already exists")
            
    except Exception as e:
        print(f"Error adding auto_save_amount field: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_auto_save_amount_field()