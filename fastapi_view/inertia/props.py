import typing as t


class IgnoreFirstLoad:
    pass


class CallableProp:
    def __init__(self, prop: t.Any):
        self._prop = prop

    def __call__(self):
        return self._prop() if callable(self._prop) else self._prop


class OptionalProp(IgnoreFirstLoad, CallableProp):
    pass


class DeferredProp(IgnoreFirstLoad, CallableProp):
    def __init__(self, prop: t.Any, group: str = "default"):
        super().__init__(prop)

        self.group = group


class MergedProp(IgnoreFirstLoad, CallableProp):
    pass
