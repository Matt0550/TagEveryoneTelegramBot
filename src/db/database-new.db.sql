BEGIN TRANSACTION;

-- Users Table
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"user_id"	INTEGER NOT NULL UNIQUE,  -- Ensures uniqueness for the user_id
	"first_name"	TEXT NOT NULL,  -- First name must be present
	"last_name"	TEXT NOT NULL,   -- Last name must be present
	"username"	TEXT NOT NULL UNIQUE,  -- Username must be unique
	"created_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,  -- Automatically set the current timestamp
	"updated_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Auto-set on updates (trigger should update this)
	CONSTRAINT unique_user UNIQUE (user_id)  -- Adding explicit constraint for user_id uniqueness
);

-- Groups Table
CREATE TABLE IF NOT EXISTS "groups" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"group_id"	INTEGER NOT NULL UNIQUE,  -- Group ID should be unique
	"group_name"	TEXT NOT NULL,  -- Group name should always be provided
	"group_description"	TEXT,
	"group_username"	TEXT,
	"group_type"	TEXT,
	"group_members"	INTEGER,  -- Consider removing if not necessary (groups_users manages this)
	"created_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Auto-created timestamp
	"updated_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Auto-updated timestamp
	CONSTRAINT unique_group UNIQUE (group_id)  -- Adding explicit constraint for group_id uniqueness
);

-- Logs Table
CREATE TABLE IF NOT EXISTS "logs" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"group_id"	INTEGER NOT NULL,
	"action"	TEXT NOT NULL,
	"description"	TEXT,
	"datetime"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,  -- Timestamp of action
	FOREIGN KEY("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY("group_id") REFERENCES "groups"("group_id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- Groups-Users Join Table
CREATE TABLE IF NOT EXISTS "groups_users" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"group_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"datetime"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,  -- Time when the user joins
	FOREIGN KEY("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY("group_id") REFERENCES "groups"("group_id") ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT unique_group_user UNIQUE (group_id, user_id)  -- Enforces uniqueness of group-user pairs
);

-- Indexes to optimize performance
CREATE INDEX IF NOT EXISTS idx_user_id ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_group_id ON logs(group_id);
CREATE INDEX IF NOT EXISTS idx_group_user ON groups_users(group_id, user_id);

COMMIT;
