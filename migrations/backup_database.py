"""
Database Backup Script
Creates a timestamped backup of the database before migrations
"""

import shutil
import os
from datetime import datetime
from pathlib import Path


def backup_database(db_path="budget_app.db"):
    """
    Create a timestamped backup of the database file.

    Args:
        db_path: Path to the database file (relative to project root or absolute)

    Returns:
        Path to the backup file, or None if backup failed
    """
    # Get absolute path to database
    if not os.path.isabs(db_path):
        project_root = Path(__file__).parent.parent
        db_path = project_root / db_path
    else:
        db_path = Path(db_path)

    if not db_path.exists():
        print(f"Database file not found: {db_path}")
        return None

    # Create backups directory if it doesn't exist
    backups_dir = db_path.parent / "backups"
    backups_dir.mkdir(exist_ok=True)

    # Generate timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"budget_app_backup_{timestamp}.db"
    backup_path = backups_dir / backup_filename

    try:
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        print(f"[OK] Database backed up to: {backup_path}")
        print(f"     Original size: {db_path.stat().st_size:,} bytes")
        print(f"     Backup size: {backup_path.stat().st_size:,} bytes")
        return backup_path
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        return None


def restore_database(backup_path, db_path="budget_app.db"):
    """
    Restore database from a backup file.

    Args:
        backup_path: Path to the backup file
        db_path: Path to restore to (default: budget_app.db)

    Returns:
        True if restore succeeded, False otherwise
    """
    backup_path = Path(backup_path)

    if not backup_path.exists():
        print(f"Backup file not found: {backup_path}")
        return False

    # Get absolute path to database
    if not os.path.isabs(db_path):
        project_root = Path(__file__).parent.parent
        db_path = project_root / db_path
    else:
        db_path = Path(db_path)

    try:
        shutil.copy2(backup_path, db_path)
        print(f"[OK] Database restored from: {backup_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Restore failed: {e}")
        return False


def list_backups():
    """List all available database backups."""
    project_root = Path(__file__).parent.parent
    backups_dir = project_root / "backups"

    if not backups_dir.exists():
        print("No backups directory found.")
        return []

    backups = sorted(backups_dir.glob("budget_app_backup_*.db"), reverse=True)

    if not backups:
        print("No backups found.")
        return []

    print(f"Found {len(backups)} backup(s):")
    for backup in backups:
        size = backup.stat().st_size
        print(f"  - {backup.name} ({size:,} bytes)")

    return backups


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "backup":
            backup_database()
        elif command == "list":
            list_backups()
        elif command == "restore" and len(sys.argv) > 2:
            restore_database(sys.argv[2])
        else:
            print("Usage:")
            print("  python backup_database.py backup   - Create a backup")
            print("  python backup_database.py list     - List all backups")
            print("  python backup_database.py restore <path>  - Restore from backup")
    else:
        # Default: create a backup
        backup_database()
