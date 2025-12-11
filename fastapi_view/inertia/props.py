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


class MergeProp(IgnoreFirstLoad, CallableProp):
    """
    A property that merges with existing client-side data during partial reloads.

    Equivalent to Laravel's MergeProp class.
    """

    def __init__(self, prop: t.Any):
        super().__init__(prop)

        self._deep_merge: bool = False
        self._append_mode: bool = True  # True = append, False = prepend
        self._appends_at_paths: list[str] = []
        self._prepends_at_paths: list[str] = []
        self._match_on: list[str] = []

    def deep_merge(self) -> "MergeProp":
        """Enable deep (recursive) merging."""
        self._deep_merge = True

        return self

    def append(
        self,
        paths: bool | str | list[str] = True,
        match_on: str | None = None,
    ) -> "MergeProp":
        """
        Configure append behavior.

        Args:
            paths: True for root append, False to disable, or specific path(s)
            match_on: Field name to match items on (prevents duplicates)
        """
        self._configure_merge_direction(
            is_append=True,
            paths=paths,
            target_paths=self._appends_at_paths,
        )
        self._add_match_field(match_on)

        return self

    def prepend(
        self,
        paths: bool | str | list[str] = True,
        match_on: str | None = None,
    ) -> "MergeProp":
        """
        Configure prepend behavior.

        Args:
            paths: True for root prepend, False to disable, or specific path(s)
            match_on: Field name to match items on (prevents duplicates)
        """
        self._configure_merge_direction(
            is_append=False,
            paths=paths,
            target_paths=self._prepends_at_paths,
        )
        self._add_match_field(match_on)

        return self

    def _configure_merge_direction(
        self,
        is_append: bool,
        paths: bool | str | list[str],
        target_paths: list[str],
    ) -> None:
        """
        Internal helper to configure merge direction (append/prepend).

        Args:
            is_append: True for append, False for prepend
            paths: Boolean flag or path list
            target_paths: List to store paths
        """
        if paths is True:
            self._append_mode = is_append
        elif paths is False:
            self._append_mode = not is_append
        else:
            path_list = [paths] if isinstance(paths, str) else paths
            target_paths.extend(path_list)

    def _add_match_field(self, match_on: str | None) -> None:
        """Add a field to match on for array merging."""
        if match_on:
            self._match_on.append(match_on)

    def should_merge(self) -> bool:
        """Check if property should be merged (always True for MergeProp)."""
        return True

    def should_deep_merge(self) -> bool:
        """Check if property should be deep merged."""
        return self._deep_merge

    def matches_on(self) -> list[str]:
        """Get fields to match on for array merging."""
        return self._match_on

    def appends_at_root(self) -> bool:
        """Check if should append at root level."""
        return self._append_mode and not self._appends_at_paths

    def prepends_at_root(self) -> bool:
        """Check if should prepend at root level."""
        return not self._append_mode and not self._prepends_at_paths

    def appends_at_paths(self) -> list[str]:
        """Get paths to append at."""
        return self._appends_at_paths

    def prepends_at_paths(self) -> list[str]:
        """Get paths to prepend at."""
        return self._prepends_at_paths
