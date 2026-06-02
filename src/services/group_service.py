from collections.abc import Sequence

from sqlmodel import Session, select

from models_all.group import Group, GroupCreate, GroupUpdate
from repositories.group_repository import GroupRepository
from utils.pagination import PaginationParams


class GroupService:
    def __init__(self, session: Session, repository: GroupRepository):
        self.session = session
        self.repository = repository

    def get_groups_of_user(
        self, user_id: int, params: PaginationParams
    ) -> tuple[Sequence[Group], int]:
        return self.repository.get_groups_of_user(self.session, user_id, params)

    def remove_user_from_group(self, group_id: int, user_id: int) -> None:
        return self.repository.remove_user_from_group(self.session, group_id, user_id)

    @staticmethod
    def get_or_create_group(session: Session, group_in: GroupCreate) -> Group:

        group_repo = GroupRepository()
        statement = select(Group).where(Group.telegram_id == int(group_in.telegram_id))
        group = session.exec(statement).first()
        if not group:
            group = Group.model_validate(group_in)
            group_repo.create(session, group)
        else:
            group_update = GroupUpdate(
                telegram_id=group_in.telegram_id,
                group_name=group_in.group_name,
                group_description=group_in.group_description,
                group_username=group_in.group_username,
                group_type=group_in.group_type,
                group_members=group_in.group_members,
            )
            group_repo.update(
                session, group, group_update.model_dump(exclude_unset=True)
            )
        return group

    @staticmethod
    def get_all_groups(session: Session) -> Sequence[Group]:
        return GroupRepository().get_all(session)

    @staticmethod
    def update_group(session: Session, telegram_id: int, **kwargs) -> Group | None:
        repo = GroupRepository()
        group = repo.get_by_telegram_id(session, telegram_id)
        if group:
            return repo.update(session, group, kwargs)
        return None

    @staticmethod
    def delete_group(session: Session, telegram_id: int) -> None:
        repo = GroupRepository()
        group = repo.get_by_telegram_id(session, telegram_id)
        if group:
            repo.delete(session, group.id)
