from enum import IntFlag, auto


class Permission(IntFlag):
    SYSTEM = auto()


ALL_PERMISSIONS = Permission.SYSTEM
