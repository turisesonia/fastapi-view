from enum import StrEnum


class InertiaHeader(StrEnum):
    INERTIA = "X-Inertia"
    INERTIA_VERSION = "X-Inertia-Version"
    INERTIA_LOCATION = "X-Inertia-Location"
    PARTIAL_ONLY = "X-Inertia-Partial-Data"
    PARTIAL_EXCEPT = "X-Inertia-Partial-Except"
    PARTIAL_COMPONENT = "X-Inertia-Partial-Component"

    @classmethod
    def values(cls):
        return [member.value for member in cls]
