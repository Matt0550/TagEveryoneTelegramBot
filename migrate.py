# Migrade from old db to new
import sqlite3
import json
import os
from datetime import datetime

dbPath = os.path.join(os.path.dirname(__file__), 'database.db')
dbPathNew = os.path.join(os.path.dirname(__file__), 'database-new.db')

# Iterete all groups of old db
def iterateGroups():
    # Create a sqlite3 connection
    conn = sqlite3.connect(dbPath, check_same_thread=False)
    # Create a cursor
    c = conn.cursor()
    # Get all groups from "groups" table
    c.execute("SELECT group_id FROM groups")
    # Fetch all the data
    data = c.fetchall()
    # Close the connection
    conn.close()
    # Return the data
    return data

def iterateMembers(group_id):
    # Create a sqlite3 connection
    conn = sqlite3.connect(dbPath, check_same_thread=False)
    # Create a cursor
    c = conn.cursor()
    # Get all members id from "groups_users" table
    c.execute("SELECT members_id FROM groups WHERE group_id=?", (group_id,))
    # Fetch all the data
    data = c.fetchall()
    # Convert the data to json
    data = json.loads(data[0][0])
    # Close the connection
    conn.close()
    # Return the data
    return data


# Main
def main():
    oldGroups = iterateGroups()
    print(oldGroups)
    # Create a sqlite3 connection
    conn = sqlite3.connect(dbPathNew, check_same_thread=False)
    # Create a cursor
    c = conn.cursor()
    # Create one group at a time. The old db cotains only the group id. So set to null the other fields
    for group in oldGroups:
        c.execute("INSERT INTO groups (group_id, group_name, group_description, group_username, group_type, group_members) VALUES (?, ?, ?, ?, ?, ?)", (group[0], None, None, None, None, None))
        conn.commit()

    # Iterate all groups
    for group in oldGroups:
        print("Migrating group: " + str(group[0]))
        # Get all members id from "groups_users" table
        members = iterateMembers(group[0])
        # Iterate all members
        for member in members:

            # Create a sqlite3 connection
            conn = sqlite3.connect(dbPathNew, check_same_thread=False)
            # Create a cursor
            c = conn.cursor()
            # Insert data into users
            c.execute("INSERT INTO users (user_id, first_name, last_name, username, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", (member, None, None, None, datetime.now(), None))
            conn.commit()

            # Insert data into "groups_users" table
            c.execute("INSERT INTO groups_users (group_id, user_id, datetime) VALUES (?, ?, ?)", (group[0], member, datetime.now()))
            conn.commit()
            # Close the connection
            conn.close()

    # Close the connection
    conn.close()

# Run the main function
if __name__ == "__main__":
    main()