import asyncio
import html
import uuid

from sqlmodel import Session
from telegram import Bot, Update

from models_all.user import User, UserCreate
from repositories.group_repository import GroupRepository
from repositories.user_repository import UserRepository
from services.cache_service import get_cache
from services.group_service import GroupService
from services.user_service import UserService
from utils.config import settings


class MentionService:
    @staticmethod
    async def fetch_user_live(
        session: Session,
        uid: int,
        group_id: uuid.UUID,
        group_telegram_id: int,
        user_service: UserService,
        group_service: GroupService,
        bot: Bot | None = None,
        update: Update | None = None,
        db_user: User | None = None,
    ) -> tuple[int, str | None, User | None]:
        """
        Perform a live lookup using Telegram API.
        Returns a tuple of (uid, username, db_user).
        """
        try:
            if update and update.message:
                member = await update.message.chat.get_member(uid)
            elif bot:
                member = await bot.get_chat_member(group_telegram_id, uid)
            else:
                return uid, (db_user.username if db_user else None), db_user

            if member.user.username is not None:
                db_user = user_service.get_or_create_user(
                    session,
                    UserCreate(
                        user_id=uid,
                        username=member.user.username,
                        first_name=member.user.first_name,
                        last_name=member.user.last_name,
                    ),
                )
            return uid, member.user.username, db_user
        except Exception as e:
            error_message_lower = str(e).lower()
            if (
                "member not found" in error_message_lower
                or "participant_id_invalid" in error_message_lower
                or "user not found" in error_message_lower
            ):
                group_service.remove_user_from_group(group_id, uid)
                return uid, "SKIP", db_user

            # Fallback to DB cache even if stale
            if db_user:
                return uid, db_user.username, db_user
            return uid, None, None

    @staticmethod
    async def build_mentions(
        session: Session,
        group_id: uuid.UUID,
        group_telegram_id: int,
        user_ids: set[int],
        exclude_user_id: int | None = None,
        bot: Bot | None = None,
        update: Update | None = None,
        plain_text: bool = False,
    ) -> list[str]:
        """
        Builds a list of mention strings for the given users.
        """
        user_service = UserService(session, UserRepository())
        group_service = GroupService(session, GroupRepository())

        target_uids = set(user_ids)
        if exclude_user_id and exclude_user_id in target_uids:
            target_uids.remove(exclude_user_id)

        # 1. Bulk fetch users from DB (fallback source for username + name fields)
        db_users = user_service.get_users_by_ids(target_uids)
        db_user_map = {u.user_id: u for u in db_users}

        # 2. Probe Redis for cached usernames; misses go to live lookup
        cache = get_cache()
        resolved_data = {}  # dict of uid -> tuple(username, db_user)
        live_lookup_tasks = []

        for uid in target_uids:
            db_user = db_user_map.get(uid)
            cached_username = await cache.get(f"user:{uid}:username")
            if cached_username is not None and db_user and db_user.username:
                resolved_data[uid] = (cached_username, db_user)
            else:
                live_lookup_tasks.append((uid, db_user))

        # 3. Perform concurrent API lookups with Semaphore
        if live_lookup_tasks:
            semaphore = asyncio.Semaphore(10)

            async def _bounded_fetch(lookup_uid: int, user_obj: User | None):
                async with semaphore:
                    return await MentionService.fetch_user_live(
                        session=session,
                        uid=lookup_uid,
                        group_id=group_id,
                        group_telegram_id=group_telegram_id,
                        user_service=user_service,
                        group_service=group_service,
                        bot=bot,
                        update=update,
                        db_user=user_obj,
                    )

            coroutines = [_bounded_fetch(u, obj) for u, obj in live_lookup_tasks]
            results = await asyncio.gather(*coroutines)

            for res_uid, username, res_db_user in results:
                resolved_data[res_uid] = (username, res_db_user)
                if username and username != "SKIP":
                    await cache.set(
                        f"user:{res_uid}:username",
                        username,
                        ttl=settings.CACHE_USERNAME_TTL,
                    )

        # 4. Format mentions
        mentions = []

        # Preserve original order somewhat (by iterating over original user_ids)
        for uid in user_ids:
            if exclude_user_id and uid == exclude_user_id:
                if not plain_text:
                    mentions.append("You")
                continue

            username, db_user = resolved_data.get(uid, (None, None))

            if username == "SKIP":
                continue

            # Best available display name from the DB record (no @username).
            display_name = None
            if db_user and db_user.first_name:
                display_name = db_user.first_name
                if db_user.last_name:
                    display_name += f" {db_user.last_name}"

            if plain_text:
                if username:
                    mentions.append(f"@{username}")
                elif display_name:
                    mentions.append(display_name)
                else:
                    mentions.append(f"ID: {uid}")
            else:
                if username:
                    label = f"@{username}"
                elif display_name:
                    # Escape: first/last names are user-controlled and the
                    # message is sent with parse_mode=HTML.
                    label = html.escape(display_name)
                else:
                    label = "👤"
                # tg://user?id=... pings the member even without a @username.
                mentions.append(f"<a href='tg://user?id={uid}'>{label}</a>")

        return mentions
