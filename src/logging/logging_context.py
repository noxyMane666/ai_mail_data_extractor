from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import ClassVar, Iterator


@dataclass(frozen=True)
class RequestContext:
    NO_VALUE: ClassVar[str] = "-"
    _var: ClassVar[ContextVar["RequestContext | None"]] = ContextVar("request_context", default=None)

    request_id: str = NO_VALUE
    method: str = NO_VALUE
    path: str = NO_VALUE

    @classmethod
    def current(cls) -> "RequestContext":
        return cls._var.get() or cls()

    @classmethod
    @contextmanager
    def bind(cls, request_id: str, method: str, path: str) -> Iterator[None]:
        context = cls(request_id or cls.NO_VALUE, method or cls.NO_VALUE, path or cls.NO_VALUE)
        token = cls._var.set(context)
        try:
            yield
        finally:
            cls._var.reset(token)
