import typing

import keyring
from jaraco.classes import properties
from keyring.backend import KeyringBackend
from keyring.errors import KeyringLocked

from lib2fas._security import KeyringManager


class LockedKeyring(KeyringBackend):
    def set_password(self, service: str, username: str, password: str) -> None:
        raise KeyringLocked("1")

    def get_password(self, service: str, username: str) -> typing.Optional[str]:
        raise KeyringLocked("2")

    def delete_password(self, service: str, username: str) -> None:
        raise KeyringLocked("3")

    @properties.classproperty
    def priority(self) -> typing.Union[int, float]:
        return 0


def test_breaking_keyring():
    failing = LockedKeyring()
    keyring.set_keyring(failing)

    manager = KeyringManager.or_dummy()

    print(manager.cleanup_keyring())
    print(manager.retrieve_credentials("test"))
