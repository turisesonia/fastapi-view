from enum import StrEnum


class Header(StrEnum):
    X_INERTIA = "X-Inertia"
    X_INERTIA_VERSION = "X-Inertia-Version"
    X_INERTIA_LOCATION = "X-Inertia-Location"
    X_INERTIA_PARTIAL_DATA = "X-Inertia-Partial-Data"
    X_INERTIA_PARTIAL_COMPONENT = "X-Inertia-Partial-Component"

    @classmethod
    def values(cls):
        return [member.value for member in cls]
