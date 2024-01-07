BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL UNIQUE,
	"first_name"	TEXT,
	"last_name"	TEXT,
	"username"	TEXT,
	"created_at"	TEXT NOT NULL,
	"updated_at"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "groups" (
	"id"	INTEGER NOT NULL,
	"group_id"	INTEGER NOT NULL UNIQUE,
	"group_name"	TEXT,
	"group_description"	TEXT,
	"group_username"	TEXT,
	"group_type"	TEXT,
	"group_members"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "logs" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER,
	"group_id"	INTEGER,
	"action"	TEXT NOT NULL,
	"description"	TEXT,
	"datetime"	TEXT,
	FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
	FOREIGN KEY("group_id") REFERENCES "groups"("group_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "groups_users" (
	"id"	INTEGER NOT NULL,
	"group_id"	INTEGER,
	"user_id"	INTEGER,
	"datetime"	TEXT,
	FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
	FOREIGN KEY("group_id") REFERENCES "groups"("group_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
