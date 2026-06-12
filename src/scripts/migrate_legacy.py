#!/usr/bin/env python3
"""CLI migrator: legacy V1 SQLite database -> V2 SQLModel schema.

Reads the old raw-SQLite database (schema in ``src/db/database-new.db.sql``,
historically accessed through ``src/db/databaseNew.py``) and writes the data
into the configured V2 database (see :mod:`utils.config` /
:mod:`utils.session_manager`).

Old -> new mapping:

* ``users``        -> ``users``
* ``groups``       -> ``groups`` (old ``group_id`` -> ``telegram_id``)
* ``groups_users`` -> each group's **system "everyone" list** (a ``TagList``
  with ``trigger_name="everyone"``, ``is_system=True``) + ``list_users`` rows,
  mirroring ``GroupService._ensure_everyone_list`` and the live ``/in`` command.
* ``logs``         -> ``logs`` (old ``group_id`` Telegram id remapped to the new
  ``groups.id`` UUID; ``None`` when the group is absent).

Usage::

    python -m scripts.migrate_legacy all
    python -m scripts.migrate_legacy group  <telegram_group_id>
    python -m scripts.migrate_legacy groups <id> <id> ...

Run it from the ``src`` directory, or anywhere (it bootstraps ``sys.path``).

Notes:
* The V2 schema must already exist (run ``alembic upgrade head`` first); this
  tool inserts rows, it does not create tables.
* Users / groups / memberships are migrated idempotently (existing rows are
  skipped). Logs have no natural key and are insert-only -> re-running may
  duplicate them. Use ``--no-logs`` to skip them.
"""

import argparse
import os
import sqlite3
import sys
from datetime import UTC, datetime

# --- bootstrap: make `src` importable (same idiom as bot/main.py) ------------
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sqlmodel import Session, select  # noqa: E402

from models_all import Group, ListUser, Log, TagList, User  # noqa: E402
from repositories.list_repository import ListRepository  # noqa: E402
from utils.session_manager import engine  # noqa: E402

DEFAULT_SOURCE_DB = os.path.join(SRC_DIR, "db", "input", "database-new.db")

# Everyone-list spec — mirrors GroupService._ensure_everyone_list.
EVERYONE_TRIGGER = "everyone"
EVERYONE_DEFAULTS = {
    "name": "Everyone",
    "trigger_name": EVERYONE_TRIGGER,
    "description": "Default list for everyone in the group",
    "aliases": ["all"],
    "is_system": True,
}

_STAT_KEYS = ("users", "groups", "lists", "memberships", "logs")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def parse_dt(value) -> datetime | None:
    """Parse a legacy TEXT datetime into a tz-aware UTC datetime (None-safe)."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        dt_val = value
    else:
        text = str(value).strip()
        try:
            dt_val = datetime.fromisoformat(text)
        except ValueError:
            dt_val = None
            for fmt in (
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
            ):
                try:
                    dt_val = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue
        if dt_val is None:
            return None
    if dt_val.tzinfo is None:
        dt_val = dt_val.replace(tzinfo=UTC)
    return dt_val.astimezone(UTC)


def to_int(value) -> int | None:
    """Coerce a legacy value to int, tolerating None / empty / non-numeric."""
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def open_source(path: str) -> sqlite3.Connection:
    if not os.path.exists(path):
        sys.exit(f"ERROR: source database not found: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    _validate_source(conn, path)
    return conn


def _validate_source(conn: sqlite3.Connection, path: str) -> None:
    """Ensure the source really is a legacy V1 database, not an already-migrated
    V2 one (both historically share the ``database-new.db`` filename)."""
    tables = {
        r["name"]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    required = {"users", "groups", "groups_users", "logs"}
    missing = required - tables
    if missing:
        hint = ""
        if "list_users" in tables or "tag_lists" in tables:
            hint = (
                "\nThis looks like an already-migrated V2 database "
                "(found tag_lists/list_users)."
            )
        sys.exit(
            f"ERROR: {path} does not look like a legacy V1 database.\n"
            f"Missing expected table(s): {', '.join(sorted(missing))}.{hint}"
        )
    group_cols = {r["name"] for r in conn.execute("PRAGMA table_info('groups')")}
    if "group_id" not in group_cols:
        sys.exit(
            f"ERROR: {path} 'groups' table has no 'group_id' column — "
            "this is not the legacy V1 schema."
        )


def _new_stats() -> dict[str, dict[str, int]]:
    return {key: {"inserted": 0, "skipped": 0} for key in _STAT_KEYS}


def _ensure_everyone_list(
    session: Session, list_repo: ListRepository, group: Group, stats: dict
) -> TagList:
    """Get-or-create the system "everyone" list for ``group``."""
    everyone = list_repo.get_by_trigger_name(session, group.id, EVERYONE_TRIGGER)
    if everyone is None:
        everyone = TagList(group_id=group.id, **EVERYONE_DEFAULTS)
        session.add(everyone)
        stats["lists"]["inserted"] += 1
    else:
        stats["lists"]["skipped"] += 1
    return everyone


# --------------------------------------------------------------------------- #
# Core migration
# --------------------------------------------------------------------------- #
def migrate(
    source_db: str,
    mode: str,
    group_ids: list[int] | None,
    include_logs: bool,
    dry_run: bool,
    update_existing: bool,
) -> None:
    # Guard: old and new SQLite share the same default filename. Refuse to read
    # and write the same file with two different schemas.
    if engine.url.get_backend_name() == "sqlite" and engine.url.database:
        target_path = os.path.abspath(engine.url.database)
        if target_path == os.path.abspath(source_db):
            sys.exit(
                "ERROR: source and target SQLite databases are the same file:\n"
                f"  {target_path}\n"
                "Migrate into MySQL (set DB_TYPE=mysql) or pass a distinct "
                "--source-db / target path (e.g. a copy of the legacy file)."
            )

    src = open_source(source_db)
    list_repo = ListRepository()
    stats = _new_stats()

    # None => every group; otherwise the explicitly selected Telegram group ids.
    selected: set[int] | None = set(group_ids) if group_ids else None

    try:
        with Session(engine) as session:
            _migrate_users(src, session, selected, include_logs, update_existing, stats)
            existing_user_ids = set(session.exec(select(User.user_id)).all())
            migrated_groups = _migrate_groups(
                src, session, selected, update_existing, stats
            )
            tg_to_group = {g.telegram_id: g for g in migrated_groups}
            _migrate_memberships(
                src, session, list_repo, migrated_groups, existing_user_ids, stats
            )
            if include_logs:
                _migrate_logs(src, session, selected, tg_to_group, stats)

            if dry_run:
                session.rollback()
            else:
                session.commit()
    finally:
        src.close()

    _print_summary(mode, group_ids, include_logs, dry_run, stats)


def _migrate_users(
    src: sqlite3.Connection,
    session: Session,
    selected: set[int] | None,
    include_logs: bool,
    update_existing: bool,
    stats: dict,
) -> None:
    if selected is None:
        rows = src.execute("SELECT * FROM users").fetchall()
    else:
        ph = ",".join("?" * len(selected))
        params = tuple(selected)
        wanted = {
            r["user_id"]
            for r in src.execute(
                f"SELECT DISTINCT user_id FROM groups_users WHERE group_id IN ({ph})",
                params,
            ).fetchall()
            if r["user_id"] is not None
        }
        if include_logs:
            wanted |= {
                r["user_id"]
                for r in src.execute(
                    f"SELECT DISTINCT user_id FROM logs "
                    f"WHERE group_id IN ({ph}) AND user_id IS NOT NULL",
                    params,
                ).fetchall()
            }
        if wanted:
            uph = ",".join("?" * len(wanted))
            rows = src.execute(
                f"SELECT * FROM users WHERE user_id IN ({uph})", tuple(wanted)
            ).fetchall()
        else:
            rows = []

    existing = set(session.exec(select(User.user_id)).all())
    for row in rows:
        uid = row["user_id"]
        if uid in existing:
            if update_existing:
                user = session.exec(select(User).where(User.user_id == uid)).first()
                user.first_name = row["first_name"]
                user.last_name = row["last_name"]
                user.username = row["username"]
                session.add(user)
            stats["users"]["skipped"] += 1
            continue
        kwargs = {
            "user_id": uid,
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "username": row["username"],
        }
        created = parse_dt(row["created_at"])
        if created:
            kwargs["created_at"] = created
        updated = parse_dt(row["updated_at"])
        if updated:
            kwargs["updated_at"] = updated
        session.add(User(**kwargs))
        existing.add(uid)
        stats["users"]["inserted"] += 1


def _migrate_groups(
    src: sqlite3.Connection,
    session: Session,
    selected: set[int] | None,
    update_existing: bool,
    stats: dict,
) -> list[Group]:
    if selected is None:
        rows = src.execute("SELECT * FROM groups").fetchall()
    else:
        ph = ",".join("?" * len(selected))
        rows = src.execute(
            f"SELECT * FROM groups WHERE group_id IN ({ph})", tuple(selected)
        ).fetchall()

    tg_to_group = {g.telegram_id: g for g in session.exec(select(Group)).all()}
    in_scope: list[Group] = []
    for row in rows:
        tg = row["group_id"]
        group = tg_to_group.get(tg)
        if group is None:
            group = Group(
                telegram_id=tg,
                group_name=row["group_name"],
                group_description=row["group_description"],
                group_username=row["group_username"],
                group_type=row["group_type"],
                group_members=to_int(row["group_members"]),
            )
            session.add(group)
            tg_to_group[tg] = group
            stats["groups"]["inserted"] += 1
        else:
            if update_existing:
                group.group_name = row["group_name"]
                group.group_description = row["group_description"]
                group.group_username = row["group_username"]
                group.group_type = row["group_type"]
                group.group_members = to_int(row["group_members"])
                session.add(group)
            stats["groups"]["skipped"] += 1
        in_scope.append(group)
    return in_scope


def _migrate_memberships(
    src: sqlite3.Connection,
    session: Session,
    list_repo: ListRepository,
    groups: list[Group],
    existing_user_ids: set[int],
    stats: dict,
) -> None:
    for group in groups:
        everyone = _ensure_everyone_list(session, list_repo, group, stats)
        existing_members = set(
            session.exec(
                select(ListUser.user_id).where(
                    ListUser.list_id == everyone.id, ListUser.active == True
                )
            ).all()
        )
        rows = src.execute(
            "SELECT user_id, datetime FROM groups_users WHERE group_id = ?",
            (group.telegram_id,),
        ).fetchall()
        for row in rows:
            uid = row["user_id"]
            # Skip null members, already-linked members, and members whose user
            # row is absent from the target (list_users.user_id is a FK).
            if uid is None or uid in existing_members or uid not in existing_user_ids:
                stats["memberships"]["skipped"] += 1
                continue
            kwargs = {"list_id": everyone.id, "user_id": uid}
            created = parse_dt(row["datetime"])
            if created:
                kwargs["created_at"] = created
            session.add(ListUser(**kwargs))
            existing_members.add(uid)
            stats["memberships"]["inserted"] += 1


def _migrate_logs(
    src: sqlite3.Connection,
    session: Session,
    selected: set[int] | None,
    tg_to_group: dict[int, Group],
    stats: dict,
) -> None:
    if selected is None:
        rows = src.execute("SELECT * FROM logs").fetchall()
    else:
        ph = ",".join("?" * len(selected))
        rows = src.execute(
            f"SELECT * FROM logs WHERE group_id IN ({ph})", tuple(selected)
        ).fetchall()

    for row in rows:
        old_gid = row["group_id"]
        new_group = tg_to_group.get(old_gid) if old_gid is not None else None
        kwargs = {
            "user_id": row["user_id"],
            "group_id": new_group.id if new_group is not None else None,
            "action": row["action"],
            "description": row["description"],
        }
        created = parse_dt(row["datetime"])
        if created:
            kwargs["created_at"] = created
        session.add(Log(**kwargs))
        stats["logs"]["inserted"] += 1


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _print_summary(
    mode: str,
    group_ids: list[int] | None,
    include_logs: bool,
    dry_run: bool,
    stats: dict,
) -> None:
    scope = mode if not group_ids else f"{mode} {group_ids}"
    suffix = "  [DRY RUN - rolled back]" if dry_run else ""
    print()
    print("=" * 60)
    print(f"Migration summary ({scope}){suffix}")
    print("-" * 60)
    for key in _STAT_KEYS:
        if key == "logs" and not include_logs:
            print(f"  {key:<12} skipped (--no-logs)")
            continue
        s = stats[key]
        print(f"  {key:<12} inserted={s['inserted']:<6} skipped={s['skipped']}")
    print("=" * 60)
    if include_logs and not dry_run and stats["logs"]["inserted"]:
        print("NOTE: logs are insert-only; re-running will duplicate them.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migrate_legacy",
        description="Migrate the legacy V1 SQLite database into the V2 schema.",
        epilog=(
            "Ensure the V2 schema exists (alembic upgrade head) before running. "
            "Logs are insert-only (no natural key) - re-running may duplicate them."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source-db",
        default=DEFAULT_SOURCE_DB,
        help=f"Path to the legacy SQLite DB (default: {DEFAULT_SOURCE_DB}).",
    )
    parser.add_argument(
        "--no-logs", action="store_true", help="Skip migrating the logs table."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the full migration in a transaction, print the summary, then roll back.",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Refresh names on already-migrated users/groups instead of skipping them.",
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("all", help="Migrate all users, groups, memberships and logs.")
    p_group = sub.add_parser(
        "group", help="Migrate a single group by its Telegram group id."
    )
    p_group.add_argument("group_id", type=int)
    p_groups = sub.add_parser(
        "groups", help="Migrate multiple groups by Telegram group id."
    )
    p_groups.add_argument("group_ids", type=int, nargs="+")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "all":
        group_ids = None
    elif args.command == "group":
        group_ids = [args.group_id]
    else:
        group_ids = args.group_ids

    migrate(
        source_db=args.source_db,
        mode=args.command,
        group_ids=group_ids,
        include_logs=not args.no_logs,
        dry_run=args.dry_run,
        update_existing=args.update_existing,
    )


if __name__ == "__main__":
    main()
