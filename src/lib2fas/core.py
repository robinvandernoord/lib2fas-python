"""
This file contains the core functionality.
"""

import sys
import typing
from collections import defaultdict
from pathlib import Path
from typing import Optional

import pyjson5

from ._security import decrypt, keyring_manager
from ._types import TwoFactorAuthDetails, into_class
from .utils import flatten, fuzzy_match

T_TwoFactorAuthDetails = typing.TypeVar("T_TwoFactorAuthDetails", bound=TwoFactorAuthDetails)


class TwoFactorStorage(typing.Generic[T_TwoFactorAuthDetails]):
    """
    Container to make working with a collection of 2fas services easier.
    """

    _multidict: defaultdict[str, list[T_TwoFactorAuthDetails]]
    count: int

    def __init__(self, _klass: typing.Type[T_TwoFactorAuthDetails] = None) -> None:
        """
        Create a new instance, usually done by `new_auth_storage()`.

        Args:
            _klass: _klass is purely for annotation atm
        """
        self._multidict = defaultdict(list)  # one name can map to multiple keys
        self.count = 0

    def __len__(self) -> int:
        """
        The length of the storage is the amount of items in it.
        """
        return self.count

    def __bool__(self) -> bool:
        """
        The storage is truthy if it has any items.
        """
        return self.count > 0

    def add(self, entries: list[T_TwoFactorAuthDetails]) -> None:
        """
        Extend the storage with new items.
        """
        for entry in entries:
            name = (entry.name or "").lower()
            self._multidict[name].append(entry)

        self.count += len(entries)

    def __getitem__(self, item: str) -> "list[T_TwoFactorAuthDetails]":
        """
        Get a service via the class[property] syntax.
        """
        #
        return self._multidict[item.lower()]

    def keys(self) -> list[str]:
        """
        Return a list of services in this storage.

        Usage:
            storage.keys()
        """
        return list(self._multidict.keys())

    def items(self) -> typing.Generator[tuple[str, list[T_TwoFactorAuthDetails]], None, None]:
        """
        Loop through tuples of key and values.

        Usage:
            for key, value in storage.items(): ...
            # (like dict.items())
        """
        yield from self._multidict.items()

    def _fuzzy_find(self, find: typing.Optional[str], fuzz_threshold: int) -> list[T_TwoFactorAuthDetails]:
        if not find:
            # don't loop
            return list(self)

        all_items = self._multidict.items()

        find = find.lower()
        # if nothing found exactly, try again but fuzzy (could be slower)
        # search in key:
        fuzzy = [
            # search in key
            v
            for k, v in all_items
            if fuzzy_match(k.lower(), find) > fuzz_threshold
        ]
        if fuzzy and (flat := flatten(fuzzy)):
            return flat

        # search in value:
        # str is short, repr is json
        return [
            # search in value instead
            v
            for v in list(self)
            if fuzzy_match(repr(v).lower(), find) > fuzz_threshold
        ]

    def generate(self) -> list[tuple[str, str]]:
        """
        Create TOTP codes for all services in this storage.
        """
        return [(_.name, _.generate()) for _ in self]

    def find(
        self, target: Optional[str] = None, fuzz_threshold: int = 75
    ) -> "TwoFactorStorage[T_TwoFactorAuthDetails]":
        """
        Create a new storage object with a subset of items in this storage, filtered by the search query in 'target'.

        First, an exact search is tried and if that fails, fuzzy matching is applied.
        """
        target = (target or "").lower()
        # first try exact match:
        if items := self._multidict.get(target):
            return new_auth_storage(items)
        # else: fuzzy match:
        return new_auth_storage(self._fuzzy_find(target, fuzz_threshold))

    def all(self) -> list[T_TwoFactorAuthDetails]:
        """
        Return a list of services.
        """
        return list(self)

    def __iter__(self) -> typing.Generator[T_TwoFactorAuthDetails, None, None]:
        """
        Allows for-looping through this storage.
        """
        for entries in self._multidict.values():
            yield from entries

    def __repr__(self) -> str:
        """
        Representation for repr().
        """
        return f"<TwoFactorStorage with {len(self._multidict)} keys and {self.count} entries>"


def new_auth_storage(initial_items: list[T_TwoFactorAuthDetails] = None) -> TwoFactorStorage[T_TwoFactorAuthDetails]:
    """
    Create an instance of TwoFactorStorage and maybe load some items into it.
    """
    storage: TwoFactorStorage[T_TwoFactorAuthDetails] = TwoFactorStorage()

    if initial_items:
        storage.add(initial_items)

    return storage


def load_services(
    filename: str | Path, _max_retries: int = 0, passphrase: Optional[str] = None
) -> TwoFactorStorage[TwoFactorAuthDetails] | None:
    """
    Given a 2fas file, try to decrypt it (via stored password in keyring or by querying user) \
     and load into a TwoFactorStorage object.

     Args:
         filename: Path to a .2fas file
         _max_retries: how many password guesses are allowed? (default = unlimited)
         passphrase: password for the supplied 2fas file; leave empty to query the user.
            Note: when using the passphrase option, _max_retries is ignored and the keyring is not used.

    Returns:
        A TwoFactorStorage instance, or None if e.g. the requested .2fas file does not exist.

    Raises:
         PermissionError on invalid password.
    """
    filepath = Path(filename).expanduser()

    if not filepath.exists():
        return None

    with filepath.open() as f:
        data_raw = f.read()
        data = pyjson5.loads(data_raw)

    storage: TwoFactorStorage[TwoFactorAuthDetails] = new_auth_storage()

    if decrypted := data["services"]:
        services = into_class(decrypted, TwoFactorAuthDetails)
        storage.add(services)
        return storage

    encrypted = data["servicesEncrypted"]

    if passphrase is not None:
        # could raise PermissionError
        entries = decrypt(encrypted, passphrase)
        storage.add(entries)
        return storage
    else:
        retries = 0
        while True:
            # fmt: off
            password = (
                keyring_manager.retrieve_credentials(str(filename))
                or keyring_manager.save_credentials(str(filename))
            )
            # fmt: on

            try:
                entries = decrypt(encrypted, password)
                storage.add(entries)
                return storage
            except PermissionError as e:
                retries += 1  # only really useful for pytest
                print(e, file=sys.stderr)
                keyring_manager.delete_credentials(str(filename))

                if _max_retries and retries > _max_retries:
                    raise e
