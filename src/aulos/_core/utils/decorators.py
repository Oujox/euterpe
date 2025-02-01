import typing as t


class classproperty[T]:
    def __init__(self, method: t.Callable[..., T] | None = None) -> None:
        self.fget = method

    def __get__(self, _, cls=None) -> T:
        if self.fget is None:
            msg = "unreadable attribute"
            raise AttributeError(msg)
        return self.fget(cls)

    def getter(self, method: t.Callable[..., T]):
        self.fget = method
        return self
