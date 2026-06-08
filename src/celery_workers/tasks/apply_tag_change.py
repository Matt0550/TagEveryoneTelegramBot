"""Celery task that applies AUTO_ADD / AUTO_REMOVE rules after a Telegram tag
change.

Invoked by the bot's ``ChatMemberHandler`` whenever a member's ``tag`` field
transitions. Running this off the PTB event loop keeps the update queue
draining at line rate even when the same admin tags many members in a row.
"""

import uuid

from celery_workers.celery_app import celery_app
from celery_workers.celery_logger_base import logger
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_tag_rule_repository import ListTagRuleRepository
from repositories.list_user_repository import ListUserRepository
from services.list_rule_service import ListRuleService
from services.list_service import ListService
from utils.session_manager import Session, engine


@celery_app.task(
    bind=True,
    name="apply_tag_change",
    max_retries=3,
    default_retry_delay=5,
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def apply_tag_change(
    self,
    group_id: str,
    user_id: int,
    old_tag: str | None,
    new_tag: str | None,
) -> dict:
    """Apply AUTO_ADD / AUTO_REMOVE rules for a single tag transition.

    :param group_id: internal group UUID, serialized as string.
    :param user_id: telegram user ID whose tag changed.
    :param old_tag: normalized previous tag value, or ``None``.
    :param new_tag: normalized new tag value, or ``None``.
    :returns: dict with ``subscribed`` / ``unsubscribed`` counters.
    """
    task_id = self.request.id
    group_uuid = uuid.UUID(group_id)

    logger.info(
        f"[apply_tag_change] task_id={task_id} group={group_id} "
        f"user={user_id} old={old_tag!r} new={new_tag!r}"
    )

    if old_tag == new_tag:
        return {"subscribed": 0, "unsubscribed": 0, "skipped": True}

    session = Session(engine)
    try:
        list_repo = ListRepository()
        list_user_repo = ListUserRepository()
        group_repo = GroupRepository()
        rule_repo = ListTagRuleRepository()

        list_service = ListService(
            session=session,
            repository=list_repo,
            user_repo=list_user_repo,
            group_repo=group_repo,
        )
        rule_service = ListRuleService(
            session=session,
            repository=rule_repo,
            list_repo=list_repo,
            group_repo=group_repo,
        )

        def _safe_subscribe(uid: int, gid, lid) -> bool:
            try:
                return list_service.subscribe(uid, gid, lid)
            except Exception as exc:
                logger.warning(
                    f"[apply_tag_change] subscribe failed user={uid} list={lid}: {exc}"
                )
                return False

        def _safe_unsubscribe(uid: int, gid, lid) -> bool:
            try:
                return list_service.unsubscribe(uid, gid, lid)
            except Exception as exc:
                logger.warning(
                    f"[apply_tag_change] unsubscribe failed user={uid} list={lid}: {exc}"
                )
                return False

        stats = rule_service.apply_tag_change_sync(
            group_id=group_uuid,
            user_id=user_id,
            old_tag=old_tag,
            new_tag=new_tag,
            subscribe=_safe_subscribe,
            unsubscribe=_safe_unsubscribe,
        )

        logger.info(f"[apply_tag_change] done task_id={task_id} stats={stats}")
        return stats

    except Exception as exc:
        session.rollback()
        logger.error(
            f"[apply_tag_change] fatal task_id={task_id}: {exc}", exc_info=True
        )
        raise self.retry(exc=exc)
    finally:
        session.close()
