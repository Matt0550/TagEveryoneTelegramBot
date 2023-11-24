import sqlite3
import json
import os
from datetime import datetime

dbPath = os.path.join(os.path.dirname(__file__), 'database-new.db')
# DB
# CREATE TABLE "groups" (
# 	"id"	INTEGER NOT NULL,
# 	"group_id"	TEXT NOT NULL,
# 	"group_name"	TEXT,
# 	"group_description"	TEXT,
# 	"group_username"	TEXT,
# 	"group_type"	TEXT,
# 	"group_members"	TEXT,
# 	PRIMARY KEY("id" AUTOINCREMENT)
# )
# CREATE TABLE "groups_users" (
# 	"id"	INTEGER NOT NULL,
# 	"group_id"	INTEGER,
# 	"user_id"	INTEGER,
# 	"datetime"	TEXT,
# 	FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
# 	FOREIGN KEY("group_id") REFERENCES "groups_users"("group_id"),
# 	PRIMARY KEY("id" AUTOINCREMENT)
# )
# CREATE TABLE "users" (
# 	"id"	INTEGER NOT NULL,
# 	"user_id"	INTEGER NOT NULL,
# 	"first_name"	TEXT,
# 	"last_name"	TEXT,
# 	"username"	TEXT,
# 	"created_at"	TEXT NOT NULL,
# 	"updated_at"	TEXT,
# 	PRIMARY KEY("id" AUTOINCREMENT)
# )
class Database:
    # Function to members id from group id
    def getMembers(self, group_id):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Get all members id from "groups_users" table
        c.execute("SELECT user_id FROM groups_users WHERE group_id=?", (group_id,))
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data 
    
    # Function to insert data into database
    def insertData(self, group_id, group_name, group_description, group_username, group_type, group_members, member_id, first_name, last_name, username):
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
            # Update group data
            c.execute("UPDATE groups SET group_name=?, group_description=?, group_username=?, group_type=?, group_members=? WHERE group_id=?", (group_name, group_description, group_username, group_type, group_members, group_id))
            # Commit the changes
            conn.commit()
        else:
            # Insert group data
            c.execute("INSERT INTO groups (group_id, group_name, group_description, group_username, group_type, group_members) VALUES (?, ?, ?, ?, ?, ?)", (group_id, group_name, group_description, group_username, group_type, group_members))
            # Commit the changes
            conn.commit()

        # Check if user exists. If not create new user else update user data
        self.createUser(member_id, first_name, last_name, username)

        # Check if user id exists
        c.execute("SELECT user_id FROM groups_users WHERE user_id=? AND group_id=?", (member_id, group_id))
        # Fetch all the data
        data = c.fetchall()
        # If data already exists, append to members id new member id
        if data:
            print("[INFO] User already exists!")
            raise Exception("User already exists in group")
        else:
            # Insert user id into "groups_users" table
            c.execute("INSERT INTO groups_users (group_id, user_id, datetime) VALUES (?, ?, ?)", (group_id, member_id, datetime.now()))
            # Commit the changes
            conn.commit()

    def createUser(self, user_id, first_name, last_name, username):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()

        # Check if user exists. If not create new user else update user data
        c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        # Fetch all the data
        data = c.fetchall()
        # If data already exists, append to members id new member id
        if data:
            # Update user data
            c.execute("UPDATE users SET first_name=?, last_name=?, username=?, updated_at=? WHERE user_id=?", (first_name, last_name, username, datetime.now(), user_id))
            # Commit the changes
            conn.commit()
        else:
            # Insert user data
            c.execute("INSERT INTO users (user_id, first_name, last_name, username, created_at) VALUES (?, ?, ?, ?, ?)", (user_id, first_name, last_name, username, datetime.now()))
            # Commit the changes
            conn.commit()

    def getUser(self, user_id):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()

        # Get user data
        c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data

    # Function to delete data from database
    def deleteData(self, group_id, member_id):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Delete user from groups_users
        c.execute("DELETE FROM groups_users WHERE group_id=? AND user_id=?", (group_id, member_id))
        # If user is not in any group, delete user from users
        c.execute("DELETE FROM users WHERE user_id NOT IN (SELECT user_id FROM groups_users)")
        # Commit the changes
        conn.commit()
        # Close the connection
        conn.close()

    def getTotalGroups(self):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Get total groups
        c.execute("SELECT COUNT(*) FROM groups")
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data[0][0]

    def getTotalUsers(self):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Get total users
        c.execute("SELECT COUNT(*) FROM users")
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data[0][0]

    def getAllGroups(self):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Get all groups
        c.execute("SELECT * FROM groups")
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data

    def logEvent(self, user_id, group_id, action, description):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()
        # Insert log
        c.execute("INSERT INTO logs (user_id, group_id, action, description, datetime) VALUES (?, ?, ?, ?, ?)", (user_id, group_id, action, description, datetime.now()))
        # Commit the changes
        conn.commit()
        # Close the connection
        conn.close()

    def getHourlyLogs(self):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()

        # Get hourly logs
        c.execute("SELECT * FROM logs WHERE datetime BETWEEN datetime('now', '-1 hour') AND datetime('now')")
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data

    def getDailyLogs(self):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()

        # Get daily logs
        c.execute("SELECT * FROM logs WHERE datetime BETWEEN datetime('now', '-1 day') AND datetime('now')")
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data

    def getWeeklyLogs(self):
        # Create a sqlite3 connection
        conn = sqlite3.connect(dbPath, check_same_thread=False)
        # Create a cursor
        c = conn.cursor()

        # Get weekly logs
        c.execute("SELECT * FROM logs WHERE datetime BETWEEN datetime('now', '-7 day') AND datetime('now')")
        # Fetch all the data
        data = c.fetchall()
        # Close the connection
        conn.close()
        # Return the data
        return data

    def getLogs(self, time):
        if time == "hour":
            return self.getHourlyLogs()
        elif time == "day":
            return self.getDailyLogs()
        elif time == "week":
            return self.getWeeklyLogs()
        else:
            return None