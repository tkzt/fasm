from enum import Enum


class Environment(str, Enum):
    PROD = "prod"
    DEV = "dev"
    TEST = "test"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return super()._missing_(value)
