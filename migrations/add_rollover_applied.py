"""
Migration to add rollover_applied field to weeks table
"""

import sqlite3
import sys
from pathlib import Path

def add_rollover_applied_column():
    """Add rollover_applied column to weeks table"""
    
    # Database path
    db_path = Path(__file__).parent.parent / 'budget_app.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(weeks)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'rollover_applied' not in columns:
            print("Adding rollover_applied column to weeks table...")
            
            # Add the column with default value False
            cursor.execute("""
                ALTER TABLE weeks 
                ADD COLUMN rollover_applied BOOLEAN DEFAULT 0
            """)
            
            # Set all existing weeks to rollover_applied = True (assume they've been handled manually)
            cursor.execute("""
                UPDATE weeks 
                SET rollover_applied = 1 
                WHERE rollover_applied IS NULL OR rollover_applied = 0
            """)
            
            conn.commit()
            print("Successfully added rollover_applied column and marked existing weeks as processed")
        else:
            print("rollover_applied column already exists")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    success = add_rollover_applied_column()
    if not success:
        sys.exit(1)