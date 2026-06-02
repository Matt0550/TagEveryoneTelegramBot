import datetime
import os
import shutil


def backup_database():
    db_path = os.path.join(os.path.dirname(__file__), "input", "database-new.db")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Skipping backup.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(os.path.dirname(__file__), "input", f"database-new_backup_{timestamp}.db")

    shutil.copy2(db_path, backup_path)
    print(f"Database backed up successfully to: {backup_path}")

if __name__ == "__main__":
    backup_database()
