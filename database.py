import sqlite3
import json
from tkinter import E

# Create a sqlite3 connection
conn = sqlite3.connect('database.db', check_same_thread=False)
# Create a cursor
c = conn.cursor()

class Database:
    # Function to get all data from groups table
    def getData(self):
        # Get data from "groups" table
        c.execute("SELECT * FROM groups")
        # Fetch all the data
        data = c.fetchall()
        # Return the data
        return data

    # Function to members id from group id
    def getMembers(self, group_id):
        # Get members from "groups" table
        c.execute("SELECT members_id FROM groups WHERE group_id=?", (group_id))
        # Fetch all the data
        data = c.fetchall()
        # Return the data
        return data
    
    # Function to insert data into database
    def insertData(self, group_id, members_id):
        # Check if group id exists
        c.execute("SELECT group_id FROM groups WHERE group_id=?", (group_id,))
        # Fetch all the data
        data = c.fetchall()
        # If data already exists, append to members id new member id
        if data:
            # Get members id from "groups" table
            c.execute("SELECT members_id FROM groups WHERE group_id=?", (group_id,))
            # Fetch all the data
            data = c.fetchall()
            # Convert data to json
            data = json.loads(data[0][0])
            # Check if member id exists
            if not members_id in data:
                # Append new member id
                data.append(int(members_id))
                # Push data to database
                c.execute("UPDATE groups SET members_id=? WHERE group_id=?", (json.dumps(data), group_id))
                # Commit the changes
                conn.commit()

                print(data)
            else:
                raise Exception("Member id already exists")
        # If data doesn't exists, insert new data
        else:
            print("[INFO] Data doesn't exists!")
            # Insert data into "groups" table
            c.execute("INSERT INTO groups VALUES (?, ?)", (group_id, "[" + str(members_id) + "]"))
            # Commit the changes
            conn.commit()
        
    # Function to delete data from database
    def deleteData(self, group_id):
        # Delete data from "groups" table
        c.execute("DELETE FROM groups WHERE group_id=?", (group_id,))
        # Commit the changes
        conn.commit()
    
    # Function to update data in database
    def updateData(self, group_id, members_id):
        # Update data in "groups" table
        c.execute("UPDATE groups SET members_id=? WHERE group_id=?", (members_id, group_id))
        # Commit the changes
        conn.commit()

    # Function to close the connection
    def closeConnection(self):
        # Close the connection
        conn.close()