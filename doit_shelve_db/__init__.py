import pickle
from shelve import Shelf
from typing import Any

from .interfaces import AbstractCodec, GenericBackend

__all__ = ["PickleCodec", "GenericBackend"]

class PickleCodec(AbstractCodec):
    """
    # doit_shelve_db.PickleCodec
    A simple codec for Doit which utilizes [pickle](https://docs.python.org/3/library/pickle.html).
    Pair with ShelveDB for best results.
    """

    def encode(self, data: Any) -> bytes:
        return pickle.dumps(data)

    def decode(self, buf: bytes) -> Any:
        return pickle.loads(buf)


class ShelveDB(GenericBackend, default=Shelf({})):
    """
    # doit_shelve_db.ShelveDB
    A simple backend for Doit which utilizes [shelf](https://docs.python.org/3/library/shelve.html) and [pickle](https://docs.python.org/3/library/pickle.html).

    ### Examples & DocTests
    >>> db = ShelveDB("pickle.db")
    >>> db.set('task0', '_values_', {'one': 1, 'true': True})

    Prove the underlying data is the type we expect it to be.
    >>> assert isinstance(db.data, Shelf)

    >>> plain_data = dict(db.data)
    >>> print(plain_data)
    {'task0': {'_values_': {'one': 1, 'true': True}}}
    """

    def __init__(self, name, codec=...):
        codec = PickleCodec() # doit has no plugin point for 'codec', so we overwrite it
        super().__init__(name, codec)
