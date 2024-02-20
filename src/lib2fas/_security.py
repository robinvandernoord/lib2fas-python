"""
This file deals with the 2fas encryption and keyring integration.
"""

import base64
import getpass
import hashlib
import json
import logging
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any, Optional

import cryptography.exceptions
import keyring
import keyring.backends.SecretService
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from keyring.backend import KeyringBackend

from ._types import AnyDict, TwoFactorAuthDetails, into_class

# Suppress keyring warnings
keyring_logger = logging.getLogger("keyring")
keyring_logger.setLevel(logging.ERROR)  # Set the logging level to ERROR for keyring logger


def _decrypt(encrypted: str, passphrase: str) -> list[AnyDict]:
    # thanks https://github.com/wodny/decrypt-2fas-backup/blob/master/decrypt-2fas-backup.py
    credentials_enc, pbkdf2_salt, nonce = map(base64.b64decode, encrypted.split(":"))
    kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=pbkdf2_salt, iterations=10000)
    key = kdf.derive(passphrase.encode())
    aesgcm = AESGCM(key)
    credentials_dec = aesgcm.decrypt(nonce, credentials_enc, None)
    dec = json.loads(credentials_dec)  # type: list[AnyDict]
    if not isinstance(dec, list):  # pragma: no cover
        raise TypeError("Unexpected data structure in input file.")
    return dec


def decrypt(encrypted: str, passphrase: str) -> list[TwoFactorAuthDetails]:
    """
    Decrypt the 'servicesEncrypted' block with a passphrase into a list of TwoFactorAuthDetails instances.

    Raises:
        PermissionError
    """
    try:
        dicts = _decrypt(encrypted, passphrase)
        return into_class(dicts, TwoFactorAuthDetails)
    except cryptography.exceptions.InvalidTag as e:
        # wrong passphrase!
        raise PermissionError("Invalid passphrase for file.") from e


def hash_string(data: Any) -> str:
    """
    Hashes a string using SHA-256.
    """
    sha256 = hashlib.sha256()
    sha256.update(str(data).encode())
    return sha256.hexdigest()


PREFIX = "2fas:"


class KeyringManager:
    """
    Makes working with the keyring a bit easier.

    Stores passphrases for encrypted .2fas files in the keyring.
    When the user logs out, the keyring item is invalidated and the user is asked for the passphrase again.
    While the user stays logged in, the passphrase is then 'remembered'.
    """

    appname: str = ""
    tmp_file = Path(tempfile.gettempdir()) / ".2fas"

    def __init__(self) -> None:
        """
        See _init.
        """
        self._init()

    def _init(self) -> None:
        """
        Setup for a new instance.

        This is used instead of __init__ so you can call init again to set active appname (for pytest)
        """
        tmp_file = self.tmp_file
        # APPNAME is session specific but with global prefix for easy clean up

        if tmp_file.exists() and (session := tmp_file.read_text()) and session.startswith(PREFIX):
            # existing session
            self.appname = session
        else:
            # new session!
            session = hash_string((time.time()))  # random enough for this purpose
            self.appname = f"{PREFIX}{session}"
            tmp_file.write_text(self.appname)

    @classmethod
    def _retrieve_credentials(cls, filename: str, appname: str) -> Optional[str]:
        return keyring.get_password(appname, hash_string(filename))

    def retrieve_credentials(self, filename: str) -> Optional[str]:
        """
        Get the saved passphrase for a specific file.
        """
        return self._retrieve_credentials(filename, self.appname)

    @classmethod
    def _save_credentials(cls, filename: str, passphrase: str, appname: str) -> None:
        keyring.set_password(appname, hash_string(filename), passphrase)

    def save_credentials(self, filename: str) -> str:
        """
        Query the user for a passphrase and store it in the keyring.
        """
        passphrase = getpass.getpass(f"Passphrase for '{filename}'? ")
        self._save_credentials(filename, passphrase, self.appname)

        return passphrase

    @classmethod
    def _delete_credentials(cls, filename: str, appname: str) -> None:
        keyring.delete_password(appname, hash_string(filename))

    def delete_credentials(self, filename: str) -> None:
        """
        Remove a stored passphrase for a file.
        """
        self._delete_credentials(filename, self.appname)

    @classmethod
    def _cleanup_keyring(cls, appname: str) -> int:
        kr: keyring.backends.SecretService.Keyring | KeyringBackend = keyring.get_keyring()
        if not hasattr(kr, "get_preferred_collection"):  # pragma: no cover
            warnings.warn(f"Can't clean up this keyring backend! {type(kr)}", category=RuntimeWarning)
            return -1

        collection = kr.get_preferred_collection()

        # get old 2fas: keyring items:
        return len(
            [
                item
                for item in collection.get_all_items()
                if (
                    service := item.get_attributes().get("service", "")
                )  # must have a 'service' attribute, otherwise it's unrelated
                and service.startswith(PREFIX)  # must be a 2fas: service, otherwise it's unrelated
                and service != appname  # must not be the currently active session
            ]
        )

    def cleanup_keyring(self) -> None:
        """
        Remove all old items from the keyring.
        """
        self._cleanup_keyring(self.appname)


keyring_manager = KeyringManager()
