"""
Doit BACKEND Plugin interfaces implemented as Protocols and Abstract Base Classes.

`doit` does not define Protocols or Abstract Base Classes that specify the attributes 
a class needs to implement to a BACKEND plugin correctly. The classes below are functional 
as much as they are documentation of the above.
"""


from abc import ABC, abstractmethod
from copy import copy
from typing import Any, Type, TypeAlias, TypeVar, Generic
from pathlib import Path
from collections.abc import MutableMapping

__all__ = ["AbstractCodec", "GenericBackend"]

Key: TypeAlias = str
DB = TypeVar("DB", bound=MutableMapping)


class AbstractCodec(ABC):
    """
    Codec Interface utilized by [doit/dependency.py:Dependency](https://github.com/pydoit/doit/blob/0.36.0/doit/dependency.py#L481).

    See [doit/dependency.py:JSONCodec](https://github.com/pydoit/doit/blob/0.36.0/doit/dependency.py#L50) for example implementation.
    """

    @abstractmethod
    def encode(self, data: Any) -> bytes:
        """Encode data."""
        raise NotImplementedError()

    @abstractmethod
    def decode(self, buf: bytes) -> Any:
        """Decode data."""
        raise NotImplementedError()


class GenericBackend(Generic[DB]):
    """
    Database Interface used by
    [doit/dependency.py:Dependency](https://github.com/pydoit/doit/blob/0.36.0/doit/dependency.py#L481).
    """

    data: DB

    @classmethod
    def get_default(cls):
        "__fixme__"
        match cls._default:
            case factory if callable(factory):
                return factory()
            case obj if isinstance(obj, MutableMapping):
                # copy again, so that changes to obj don't affect other instances
                return copy(obj)
            case other:
                raise RuntimeError(f"no case handles {other!r}")

    def __init_subclass__(
        cls, default: DB | Type[DB] = dict, **extra
    ):  # pylint: disable=arguments-differ
        super().__init_subclass__(**extra)
        match default:
            case factory if callable(factory):
                cls._default = factory
            case obj if isinstance(obj, MutableMapping):
                # Copy obj to 'freeze' value at time of class creation.
                cls._default = copy(obj)
            case other:
                raise ValueError(f"{other!r} is neither callable nor instance")

    def __init__(self, name: str | Path, codec: AbstractCodec):
        """
        `Dependency` supplies 'codec' as a keyword argument when
        initializing a backend.

        Implement as...
        >>> class MyBackend(GenericBackend, default=dict):
        """
        self.filename = Path(name)
        self.codec = codec
        self.data = self.load()

    def load(self) -> DB:
        """Codec loads 'data' from source file."""
        if self.filename.is_dir():
            raise FileNotFoundError(
                f"no file at {self.filename}, found directory instead"
            )

        if not self.filename.is_file():
            cls = self.__class__
            _raw = self.codec.encode(cls.get_default())
            self.filename.write_bytes(_raw)

        raw = self.filename.read_bytes()
        return self.codec.decode(raw)

    def dump(self) -> None:
        """Codec writes self.data to source file."""
        raw = self.codec.encode(self.data)
        self.filename.write_bytes(raw)

    def get(self, task_id: Key, dependency: Key) -> Any:
        """implements __getitem__, return None to indicate a miss."""
        try:
            return self.data[task_id][dependency]
        except KeyError:
            return None

    def set(self, task_id: Key, dependency: Key, value) -> None:
        """implements __setitem__"""
        if task_id not in self.data:
            self.data[task_id] = {dependency: value}
        else:
            self.data[task_id][dependency] = value

    def remove(self, task_id: Key) -> None:
        """implements  __delitem__"""
        del self.data[task_id]

    def remove_all(self) -> None:
        """implements clear"""
        self.data.clear()

    def in_(self, task_id: Key) -> bool:
        """implements __contains__"""
        return task_id in self.data
