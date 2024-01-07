import sqlite3
import json
import os

dbPath = os.path.join(os.path.dirname(__file__), './input/database.db')

if not os.path.exists(dbPath):
    # Die
    raise Exception("Database file not found")

class Database:
    # Function to get all data from groups table
    def getData(self):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Get data from "groups" table
        c.execute("SELECT * FROM groups")
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data

    # Function to members id from group id
    def getMembers(self, group_id):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Get data from "groups" table
        c.execute("SELECT members_id FROM groups WHERE group_id=?", (group_id,))
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data
    
    # Function to insert data into database
    def insertData(self, group_id, members_id):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
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
        # Close the connection
        conn.close()
        
    # Function to delete data from database
    def deleteData(self, group_id, member_id):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Get data from "groups" table
        c.execute("SELECT members_id FROM groups WHERE group_id=?", (group_id,))
        # Fetch all the data
        data = c.fetchall()
        # Convert data to json
        data = json.loads(data[0][0])
        # Check if member id exists
        if member_id in data:
            # Delete member id
            data.remove(member_id)
            # Push data to database
            c.execute("UPDATE groups SET members_id=? WHERE group_id=?", (json.dumps(data), group_id))
            # Commit the changes
            conn.commit()
        else:
            raise Exception("Member id doesn't exists")
        # Close the connection
        conn.close()

    
    # Function to update data in database
    def updateData(self, group_id, members_id):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Update data in "groups" table
        c.execute("UPDATE groups SET members_id=? WHERE group_id=?", (members_id, group_id))
        # Commit the changes
        conn.commit()
        # Close the connection
        conn.close()
