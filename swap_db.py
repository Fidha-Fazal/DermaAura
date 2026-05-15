import os
import shutil

path = r"c:\Users\fidha\OneDrive\Desktop\DermaAura"
old_db = os.path.join(path, "database.py")
new_db = os.path.join(path, "database_new.py")

if os.path.exists(old_db):
    os.remove(old_db)
    print(f"Removed {old_db}")

if os.path.exists(new_db):
    shutil.move(new_db, old_db)
    print(f"Moved {new_db} to {old_db}")

print("Database file updated successfully!")
