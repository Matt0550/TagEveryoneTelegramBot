import uuid
from collections.abc import Iterable, Sequence

from sqlmodel import Session, select

from models_all import ListTagRule, TagList
from models_all.list_tag_rule import ListTagRuleMode
from repositories.base_repository import BaseRepository


class ListTagRuleRepository(BaseRepository[ListTagRule]):
    def __init__(self) -> None:
        super().__init__(ListTagRule)

    def get_rules_for_list(
        self, db: Session, list_id: uuid.UUID
    ) -> Sequence[ListTagRule]:
        """Return every active rule for a single list.

        :param db: database session.
        :param list_id: internal UUID of the parent ``TagList``.
        :returns: sequence of active rules.
        """
        statement = select(ListTagRule).where(
            ListTagRule.list_id == list_id,
            ListTagRule.active == True,
        )
        return db.exec(statement).all()

    def get_rules_for_lists(
        self, db: Session, list_ids: Iterable[uuid.UUID]
    ) -> dict[uuid.UUID, list[ListTagRule]]:
        """Batched variant of :meth:`get_rules_for_list`.

        :param db: database session.
        :param list_ids: iterable of list UUIDs to load rules for.
        :returns: mapping ``list_id -> [rules]``. Empty list when none exist.
        """
        ids = list(list_ids)
        result: dict[uuid.UUID, list[ListTagRule]] = {lid: [] for lid in ids}
        if not ids:
            return result
        statement = select(ListTagRule).where(
            ListTagRule.list_id.in_(ids),
            ListTagRule.active == True,
        )
        for row in db.exec(statement).all():
            result.setdefault(row.list_id, []).append(row)
        return result

    def get_rules_for_group(
        self, db: Session, group_id: uuid.UUID
    ) -> Sequence[ListTagRule]:
        """Return every active rule belonging to lists of ``group_id``.

        :param db: database session.
        :param group_id: internal UUID of the parent group.
        :returns: sequence of active rules across all of the group's lists.
        """
        statement = (
            select(ListTagRule)
            .join(TagList, TagList.id == ListTagRule.list_id)
            .where(
                TagList.group_id == group_id,
                TagList.active == True,
                ListTagRule.active == True,
            )
        )
        return db.exec(statement).all()

    def get_rules_for_group_by_modes(
        self,
        db: Session,
        group_id: uuid.UUID,
        modes: Iterable[ListTagRuleMode],
    ) -> Sequence[ListTagRule]:
        """Return rules of a group filtered by a set of modes.

        :param db: database session.
        :param group_id: internal UUID of the parent group.
        :param modes: iterable of :class:`ListTagRuleMode` values to keep.
        :returns: sequence of matching rules.
        """
        modes_list = list(modes)
        if not modes_list:
            return []
        statement = (
            select(ListTagRule)
            .join(TagList, TagList.id == ListTagRule.list_id)
            .where(
                TagList.group_id == group_id,
                TagList.active == True,
                ListTagRule.active == True,
                ListTagRule.mode.in_(modes_list),
            )
        )
        return db.exec(statement).all()

    def find_existing(
        self,
        db: Session,
        list_id: uuid.UUID,
        tag_value: str,
        mode: ListTagRuleMode,
    ) -> ListTagRule | None:
        """Lookup a rule by its natural key (list, tag, mode).

        :param db: database session.
        :param list_id: parent list UUID.
        :param tag_value: lowercased tag string.
        :param mode: rule mode.
        :returns: the matching active rule or ``None``.
        """
        statement = select(ListTagRule).where(
            ListTagRule.list_id == list_id,
            ListTagRule.tag_value == tag_value,
            ListTagRule.mode == mode,
            ListTagRule.active == True,
        )
        return db.exec(statement).first()
