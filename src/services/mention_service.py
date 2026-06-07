import uuid
from datetime import UTC, datetime, timedelta

from sqlmodel import Session
from telegram import Bot, Update

from models_all.user import UserCreate
from repositories.group_repository import GroupRepository
from repositories.user_repository import UserRepository
from services.group_service import GroupService
from services.user_service import UserService

USER_CACHE_MAX_AGE = timedelta(hours=24)


class MentionService:
    @staticmethod
    async def resolve_username(
        session: Session,
        user_service: UserService,
        group_service: GroupService,
        group_id: uuid.UUID,
        group_telegram_id: int,
        uid: int,
        bot: Bot | None = None,
        update: Update | None = None,
    ) -> str | None:
        """
        Resolve a user's username, using the DB cache when fresh enough.

        If the cached user is stale (updated_at > 24h) or missing, performs a
        Telegram API lookup and updates the DB.

        Returns the username string, or None if the user can't be resolved.
        Returns "SKIP" if the user left the group and was removed.
        """
        db_user = user_service.get_by_id(uid)

        # Check if cached data is fresh enough
        if db_user and db_user.username:
            cache_cutoff = datetime.now(UTC) - USER_CACHE_MAX_AGE
            if db_user.updated_at:
                updated_at_aware = (
                    db_user.updated_at.replace(tzinfo=UTC)
                    if db_user.updated_at.tzinfo is None
                    else db_user.updated_at
                )
                if updated_at_aware >= cache_cutoff:
                    return db_user.username
            elif db_user.created_at:
                created_at_aware = (
                    db_user.created_at.replace(tzinfo=UTC)
                    if db_user.created_at.tzinfo is None
                    else db_user.created_at
                )
                if created_at_aware >= cache_cutoff:
                    return db_user.username

        # Cache is stale or user not in DB — perform live lookup
        try:
            if update and update.message:
                member = await update.message.chat.get_member(uid)
            elif bot:
                member = await bot.get_chat_member(group_telegram_id, uid)
            else:
                return db_user.username if db_user else None

            if member.user.username is not None:
                user_service.get_or_create_user(
                    session,
                    UserCreate(
                        user_id=uid,
                        username=member.user.username,
                        first_name=member.user.first_name,
                        last_name=member.user.last_name,
                    ),
                )
            return member.user.username
        except Exception as e:
            error_message_lower = str(e).lower()
            if (
                "member not found" in error_message_lower
                or "participant_id_invalid" in error_message_lower
                or "user not found" in error_message_lower
            ):
                group_service.remove_user_from_group(group_id, uid)
                return "SKIP"

            # Fallback to DB cache even if stale
            if db_user:
                return db_user.username
            return None

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

        mentions = []
        for uid in user_ids:
            if exclude_user_id and uid == exclude_user_id:
                if not plain_text:
                    mentions.append("You")
                continue

            username = await MentionService.resolve_username(
                session,
                user_service,
                group_service,
                group_id,
                group_telegram_id,
                uid,
                bot,
                update,
            )

            if username == "SKIP":
                continue

            if plain_text:
                if username:
                    mentions.append(f"@{username}")
                else:
                    # For plain text, we ideally want the name. Let's try to get it from DB.
                    db_user = user_service.get_by_id(uid)
                    if db_user and db_user.first_name:
                        name = db_user.first_name
                        if db_user.last_name:
                            name += f" {db_user.last_name}"
                        mentions.append(name)
                    else:
                        mentions.append(f"ID: {uid}")
            else:
                if username:
                    mentions.append(f"<a href='tg://user?id={uid}'>@{username}</a>")
                else:
                    mentions.append(f"<a href='tg://user?id={uid}'>👤</a>")

        return mentions
