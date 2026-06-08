"""Business logic for :class:`ListTagRule` management and auto-routing."""

from __future__ import annotations

import uuid
from collections.abc import Iterable, Sequence

from sqlmodel import Session

from models_all import (
    ListTagRule,
    ListTagRuleItem,
)
from models_all.list_tag_rule import ListTagRuleMode
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_tag_rule_repository import ListTagRuleRepository
from services.base_service import BaseService
from services.cache_service import CacheService
from services.log_service import LogService
from utils.config import settings


class ListRuleService(BaseService):
    """Manage rules that filter and auto-route members based on Telegram tags."""

    LIST_RULES_KEY = "list_rules:{list_id}"
    GROUP_AUTO_RULES_KEY = "group_auto_rules:{group_id}"

    def __init__(
        self,
        session: Session,
        repository: ListTagRuleRepository,
        list_repo: ListRepository,
        group_repo: GroupRepository,
        log_service: LogService | None = None,
        cache: CacheService | None = None,
    ) -> None:
        """:param session: SQLModel session.
        :param repository: :class:`ListTagRuleRepository` for rule rows.
        :param list_repo: :class:`ListRepository` to validate parent lists.
        :param group_repo: :class:`GroupRepository` for group lookups.
        :param log_service: optional audit log writer.
        :param cache: optional cache service.
        """
        super().__init__(session=session, log_service=log_service, cache=cache)
        self.repository = repository
        self.list_repo = list_repo
        self.group_repo = group_repo

    @staticmethod
    def _normalize_tag(value: str) -> str:
        """Lowercase, strip and validate a tag string.

        :param value: raw input from caller.
        :returns: normalized tag.
        :raises ValueError: if the value is empty after normalization.
        """
        normalized = (value or "").strip().lower()
        if not normalized:
            raise ValueError("tag_value must be a non-empty string")
        if len(normalized) > 64:
            raise ValueError("tag_value cannot exceed 64 characters")
        return normalized

    def _check_list(self, group_id: uuid.UUID, list_id: uuid.UUID):
        """Verify a list exists and belongs to the given group.

        :param group_id: parent group UUID.
        :param list_id: list UUID.
        :raises ValueError: when the list does not exist or does not belong
            to the group.
        """
        tag_list = self.list_repo.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            raise ValueError("List not found or group ID mismatch")
        return tag_list

    async def _invalidate_caches(self, group_id: uuid.UUID, list_id: uuid.UUID) -> None:
        """Drop cached rule sets for a list and its parent group.

        :param group_id: parent group UUID.
        :param list_id: list UUID.
        """
        await self._invalidate(
            self.LIST_RULES_KEY.format(list_id=list_id),
            self.GROUP_AUTO_RULES_KEY.format(group_id=group_id),
        )

    def get_rules(
        self, group_id: uuid.UUID, list_id: uuid.UUID
    ) -> Sequence[ListTagRule]:
        """Return the active rules of a list (sync, uncached).

        :param group_id: parent group UUID.
        :param list_id: list UUID.
        :returns: sequence of active :class:`ListTagRule` rows.
        """
        self._check_list(group_id, list_id)
        return self.repository.get_rules_for_list(self.session, list_id)

    async def get_rules_cached(self, list_id: uuid.UUID) -> list[dict]:
        """Cached, serialized view of a list's rules suitable for fast filtering.

        Returns dicts (not ORM rows) so they survive JSON round-trips through
        Redis. Each dict has ``tag_value`` and ``mode`` keys.

        :param list_id: list UUID.
        :returns: list of ``{"tag_value": str, "mode": str}`` dicts.
        """

        async def _load() -> list[dict]:
            rows = self.repository.get_rules_for_list(self.session, list_id)
            return [{"tag_value": r.tag_value, "mode": r.mode.value} for r in rows]

        return (
            await self._cached(
                self.LIST_RULES_KEY.format(list_id=list_id),
                settings.CACHE_LIST_RULES_TTL,
                _load,
            )
            or []
        )

    async def replace_rules(
        self,
        admin_id: int,
        group_id: uuid.UUID,
        list_id: uuid.UUID,
        rules: Iterable[ListTagRuleItem],
    ) -> Sequence[ListTagRule]:
        """Atomically replace the rule set for a list.

        Existing active rules are soft-deleted; the provided rules are inserted
        fresh. Duplicate ``(tag_value, mode)`` pairs in the input are deduped.

        :param admin_id: telegram ID of the acting admin (for audit).
        :param group_id: parent group UUID.
        :param list_id: list UUID.
        :param rules: iterable of :class:`ListTagRuleItem` describing the new
            rule set.
        :returns: sequence of freshly inserted rules.
        """
        tag_list = self._check_list(group_id, list_id)

        normalized: list[tuple[str, ListTagRuleMode]] = []
        seen: set[tuple[str, ListTagRuleMode]] = set()
        for item in rules:
            tag_value = self._normalize_tag(item.tag_value)
            key = (tag_value, item.mode)
            if key in seen:
                continue
            seen.add(key)
            normalized.append(key)

        self.repository.soft_delete_where(self.session, ListTagRule.list_id == list_id)

        created: list[ListTagRule] = []
        for tag_value, mode in normalized:
            row = self.repository.create(
                self.session,
                ListTagRule(list_id=list_id, tag_value=tag_value, mode=mode),
            )
            created.append(row)

        self._log(
            admin_id,
            group_id,
            "REPLACE_LIST_RULES",
            f"Replaced rules for list {tag_list.name} ({len(created)} active)",
        )
        await self._invalidate_caches(group_id, list_id)
        return created

    async def delete_rule(
        self, admin_id: int, group_id: uuid.UUID, rule_id: uuid.UUID
    ) -> bool:
        """Soft-delete a single rule by ID.

        :param admin_id: telegram ID of the acting admin.
        :param group_id: parent group UUID (for authorization checks upstream).
        :param rule_id: UUID of the rule row.
        :returns: ``True`` if a rule was deleted.
        """
        rule = self.repository.get_by_id(self.session, rule_id)
        if not rule:
            return False
        tag_list = self.list_repo.get_by_id(self.session, rule.list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        success = self.repository.delete(self.session, rule_id)
        if success:
            self._log(
                admin_id,
                group_id,
                "DELETE_LIST_RULE",
                f"Deleted rule {rule.tag_value}:{rule.mode.value} "
                f"on list {tag_list.name}",
            )
            await self._invalidate_caches(group_id, rule.list_id)
        return success

    async def get_auto_rules_for_group(self, group_id: uuid.UUID) -> list[dict]:
        """Cached view of AUTO_ADD / AUTO_REMOVE rules for an entire group.

        Used by the ``ChatMemberUpdated`` handler one cache lookup per tag
        change instead of one DB query.

        :param group_id: parent group UUID.
        :returns: list of dicts with ``list_id``, ``tag_value``, ``mode``.
        """

        async def _load() -> list[dict]:
            rows = self.repository.get_rules_for_group_by_modes(
                self.session,
                group_id,
                [ListTagRuleMode.AUTO_ADD, ListTagRuleMode.AUTO_REMOVE],
            )
            return [
                {
                    "list_id": str(r.list_id),
                    "tag_value": r.tag_value,
                    "mode": r.mode.value,
                }
                for r in rows
            ]

        return (
            await self._cached(
                self.GROUP_AUTO_RULES_KEY.format(group_id=group_id),
                settings.CACHE_LIST_RULES_TTL,
                _load,
            )
            or []
        )

    def apply_tag_change_sync(
        self,
        group_id: uuid.UUID,
        user_id: int,
        old_tag: str | None,
        new_tag: str | None,
        subscribe: callable,
        unsubscribe: callable,
    ) -> dict:
        """Synchronous variant of :meth:`apply_tag_change` for Celery workers.

        Bypasses the async Redis cache and reads ``AUTO_*`` rules straight from
        the DB, the worker holds its own short-lived session, so the extra
        query is negligible and avoids running an event loop inside the task.

        :param group_id: internal UUID of the group.
        :param user_id: telegram user ID whose tag changed.
        :param old_tag: normalized previous tag, or ``None``.
        :param new_tag: normalized new tag, or ``None``.
        :param subscribe: callable ``(user_id, group_id, list_id) -> bool``.
        :param unsubscribe: callable ``(user_id, group_id, list_id) -> bool``.
        :returns: dict ``{"subscribed": int, "unsubscribed": int}`` for telemetry.
        """
        stats = {"subscribed": 0, "unsubscribed": 0}
        if old_tag == new_tag:
            return stats

        rows = self.repository.get_rules_for_group_by_modes(
            self.session,
            group_id,
            [ListTagRuleMode.AUTO_ADD, ListTagRuleMode.AUTO_REMOVE],
        )
        if not rows:
            return stats

        def _dispatch(matching_tag: str, on_auto_add, on_auto_remove) -> None:
            for r in rows:
                if r.tag_value != matching_tag:
                    continue
                if r.mode == ListTagRuleMode.AUTO_ADD:
                    on_auto_add(r.list_id)
                elif r.mode == ListTagRuleMode.AUTO_REMOVE:
                    on_auto_remove(r.list_id)

        if new_tag:
            _dispatch(
                new_tag,
                on_auto_add=lambda lid: stats.__setitem__(
                    "subscribed",
                    stats["subscribed"] + int(bool(subscribe(user_id, group_id, lid))),
                ),
                on_auto_remove=lambda lid: stats.__setitem__(
                    "unsubscribed",
                    stats["unsubscribed"]
                    + int(bool(unsubscribe(user_id, group_id, lid))),
                ),
            )

        if old_tag:
            _dispatch(
                old_tag,
                on_auto_add=lambda lid: stats.__setitem__(
                    "unsubscribed",
                    stats["unsubscribed"]
                    + int(bool(unsubscribe(user_id, group_id, lid))),
                ),
                on_auto_remove=lambda lid: stats.__setitem__(
                    "subscribed",
                    stats["subscribed"] + int(bool(subscribe(user_id, group_id, lid))),
                ),
            )
        return stats

    async def apply_tag_change(
        self,
        group_id: uuid.UUID,
        user_id: int,
        old_tag: str | None,
        new_tag: str | None,
        subscribe: callable,
        unsubscribe: callable,
    ) -> None:
        """Apply AUTO_ADD / AUTO_REMOVE rules in response to a tag change.

        Tag-set transitions:

        * gaining a tag (``new_tag`` is the new value) triggers ``AUTO_ADD``
          subscriptions and ``AUTO_REMOVE`` unsubscriptions for that tag;
        * losing a tag (``old_tag`` is dropped) reverses the previous side
          effects: undo ``AUTO_ADD`` (unsubscribe) and undo ``AUTO_REMOVE``
          (re-subscribe).

        Subscribe/unsubscribe primitives are injected to avoid cyclic imports
        with :class:`ListService`.

        :param group_id: internal UUID of the group.
        :param user_id: telegram user ID whose tag changed.
        :param old_tag: normalized previous tag, or ``None``.
        :param new_tag: normalized new tag, or ``None``.
        :param subscribe: callable ``(user_id, group_id, list_id) -> bool``.
        :param unsubscribe: callable ``(user_id, group_id, list_id) -> bool``.
        """
        if old_tag == new_tag:
            return

        rules = await self.get_auto_rules_for_group(group_id)
        if not rules:
            return

        if new_tag:
            for r in rules:
                if r["tag_value"] != new_tag:
                    continue
                list_uuid = uuid.UUID(r["list_id"])
                if r["mode"] == ListTagRuleMode.AUTO_ADD.value:
                    subscribe(user_id, group_id, list_uuid)
                elif r["mode"] == ListTagRuleMode.AUTO_REMOVE.value:
                    unsubscribe(user_id, group_id, list_uuid)

        if old_tag:
            for r in rules:
                if r["tag_value"] != old_tag:
                    continue
                list_uuid = uuid.UUID(r["list_id"])
                if r["mode"] == ListTagRuleMode.AUTO_ADD.value:
                    unsubscribe(user_id, group_id, list_uuid)
                elif r["mode"] == ListTagRuleMode.AUTO_REMOVE.value:
                    subscribe(user_id, group_id, list_uuid)
