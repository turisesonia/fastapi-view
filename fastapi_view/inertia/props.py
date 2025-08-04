import typing as t

class IgnoreFirstLoad:
    pass


class CallableProp:
    def __init__(self, prop: t.Any):
        self._prop = prop

    def __call__(self):
        return self._prop() if callable(self._prop) else self._prop


class LazyProp(IgnoreFirstLoad, CallableProp):
    pass


class OptionalProp(IgnoreFirstLoad, CallableProp):
    pass