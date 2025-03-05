import sqlite3
import os
from datetime import datetime

dbPath = os.path.join(os.path.dirname(__file__), './input/database-new.db')

# Ensure the database exists, create if not
if not os.path.exists(dbPath):
	try:
		with open(os.path.join(os.path.dirname(__file__), './database-new_structure.db'), 'r') as src_file:
			with open(dbPath, 'w') as dest_file:
				dest_file.write(src_file.read())
	except Exception as e:
		print(f"Error: Could not create database file - {e}")
		exit(1)


class Database:
	# Helper function to create a database connection using context manager
	def _connect(self):
		return sqlite3.connect(dbPath, check_same_thread=False)
	
	def getMembers(self, group_id):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT user_id FROM groups_users WHERE group_id=?", (group_id,))
			return cursor.fetchall()
	
	def insertData(self, group_id, group_name, group_description, group_username, group_type, group_members, member_id,
	               first_name, last_name, username):
		with self._connect() as conn:
			cursor = conn.cursor()
			# Insert or update group data
			cursor.execute("SELECT group_id FROM groups WHERE group_id=?", (group_id,))
			group_data = cursor.fetchall()
			if group_data:
				cursor.execute(
					"UPDATE groups SET group_name=?, group_description=?, group_username=?, group_type=?, group_members=? WHERE group_id=?",
					(group_name, group_description, group_username, group_type, group_members, group_id))
			else:
				cursor.execute(
					"INSERT INTO groups (group_id, group_name, group_description, group_username, group_type, group_members) VALUES (?, ?, ?, ?, ?, ?)",
					(group_id, group_name, group_description, group_username, group_type, group_members))
			
			# Insert or update user data
			self.createUser(member_id, first_name, last_name, username)
			
			# Check if user is already in the group
			cursor.execute("SELECT user_id FROM groups_users WHERE user_id=? AND group_id=?", (member_id, group_id))
			user_group_data = cursor.fetchall()
			if user_group_data:
				raise Exception("User already exists in group")
			else:
				cursor.execute("INSERT INTO groups_users (group_id, user_id, datetime) VALUES (?, ?, ?)",
				               (group_id, member_id, datetime.now()))
			conn.commit()
	
	def createUser(self, user_id, first_name, last_name, username):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
			user_data = cursor.fetchall()
			if user_data:
				cursor.execute("UPDATE users SET first_name=?, last_name=?, username=?, updated_at=? WHERE user_id=?",
				               (first_name, last_name, username, datetime.now(), user_id))
			else:
				cursor.execute(
					"INSERT INTO users (user_id, first_name, last_name, username, created_at) VALUES (?, ?, ?, ?, ?)",
					(user_id, first_name, last_name, username, datetime.now()))
			conn.commit()
	
	def getUser(self, user_id):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
			return cursor.fetchall()
	
	def getGroupsOfUser(self, user_id):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM groups WHERE group_id IN (SELECT group_id FROM groups_users WHERE user_id=?)",
			               (user_id,))
			return cursor.fetchall()
	
	def deleteGroup(self, group_id):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("DELETE FROM groups WHERE group_id=?", (group_id,))
			cursor.execute("DELETE FROM groups_users WHERE group_id=?", (group_id,))
			cursor.execute("DELETE FROM users WHERE user_id NOT IN (SELECT user_id FROM groups_users)")
			conn.commit()
	
	def updateGroupInfo(self, group_id, group_name, group_description, group_username, group_type, group_members):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute(
				"UPDATE groups SET group_name=?, group_description=?, group_username=?, group_type=?, group_members=? WHERE group_id=?",
				(group_name, group_description, group_username, group_type, group_members, group_id))
			conn.commit()
	
	def deleteData(self, group_id, member_id):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("DELETE FROM groups_users WHERE group_id=? AND user_id=?", (group_id, member_id))
			cursor.execute("DELETE FROM users WHERE user_id NOT IN (SELECT user_id FROM groups_users)")
			conn.commit()
	
	def getTotalGroups(self):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT COUNT(*) FROM groups")
			return cursor.fetchone()[0]
	
	def getTotalUsers(self):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT COUNT(*) FROM users")
			return cursor.fetchone()[0]
	
	def getAllGroups(self):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM groups")
			return cursor.fetchall()
	
	def logEvent(self, user_id, group_id, action, description):
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO logs (user_id, group_id, action, description, datetime) VALUES (?, ?, ?, ?, ?)",
			               (user_id, group_id, action, description, datetime.now()))
			conn.commit()
	
	def getHourlyLogs(self):
		return self._getLogs('hour')
	
	def getDailyLogs(self):
		return self._getLogs('day')
	
	def getWeeklyLogs(self):
		return self._getLogs('week')
	
	def _getLogs(self, time_frame):
		time_intervals = {
			"hour": "-1 hour",
			"day": "-1 day",
			"week": "-7 day"
		}
		if time_frame not in time_intervals:
			return None
		
		with self._connect() as conn:
			cursor = conn.cursor()
			cursor.execute(
				f"SELECT * FROM logs WHERE datetime BETWEEN datetime('now', '{time_intervals[time_frame]}') AND datetime('now') ORDER BY datetime DESC")
			return cursor.fetchall()
	
	def getLogs(self, time):
		return {
			"hour": self.getHourlyLogs(),
			"day": self.getDailyLogs(),
			"week": self.getWeeklyLogs()
		}.get(time, None)
