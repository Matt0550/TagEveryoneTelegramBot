from enum import StrEnum


class Role(StrEnum):
    SUPER_ADMIN = "super_admin"
    GROUP_ADMIN = "group_admin"
    USER = "user"
    API_CLIENT = "api_client"


class Permission(StrEnum):
    MANAGE_LISTS = "manage_lists"
    TRIGGER_MENTIONS = "trigger_mentions"
    MANAGE_EXCLUSIONS = "manage_exclusions"
