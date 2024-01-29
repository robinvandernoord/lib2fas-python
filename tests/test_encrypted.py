import pytest

from src.lib2fas import load_services
from src.lib2fas._security import KeyringManager, keyring_manager

from ._shared import CWD

FILENAME = str(CWD / "2fas-demo-pass.2fas")
PASSWORD = "test"


@pytest.fixture()
def clean_keyring():
    # manager classmethods without an instance will clear even active entries.
    KeyringManager.tmp_file.unlink(missing_ok=True)
    KeyringManager._cleanup_keyring("")

    keyring_manager._init()
    # and also the active manager (idk why but seems necessary):
    keyring_manager.cleanup_keyring()


@pytest.fixture
def getpass_wrong(clean_keyring, monkeypatch):
    """Did the file we wrote actually become json."""
    monkeypatch.setattr("getpass.getpass", lambda _: "***")


@pytest.fixture
def getpass_correct(clean_keyring, monkeypatch):
    """Did the file we wrote actually become json."""
    monkeypatch.setattr("getpass.getpass", lambda _: PASSWORD)


@pytest.fixture
def getpass_empty(monkeypatch):
    """Did the file we wrote actually become json."""
    monkeypatch.setattr("getpass.getpass", lambda _: "")


def test_wrong_pass(getpass_wrong):
    with pytest.raises(PermissionError):
        assert not load_services(FILENAME, _max_retries=1)


def test_pass_noninteractive(getpass_wrong):
    with pytest.raises(PermissionError):
        assert not load_services(FILENAME, _max_retries=1, passphrase="")

    services = load_services(FILENAME, _max_retries=1, passphrase=PASSWORD)
    assert services


def test_right_pass(getpass_correct):
    services = load_services(FILENAME)
    assert services


def test_from_keyring(getpass_empty):
    # note: `test_right_pass` MUST be executed right before!
    services = load_services(FILENAME, _max_retries=1)
    assert services


def test_reload_keyring():
    # must also be executed after `test_right_pass` and/or `test_from_keyring`
    new_manager = KeyringManager()

    assert new_manager != keyring_manager
    assert new_manager.appname == keyring_manager.appname
