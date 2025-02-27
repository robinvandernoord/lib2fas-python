import pytest

from src.lib2fas import load_services
from src.lib2fas._security import DummyKeyringManager, KeyringManager, keyring_manager

from ._shared import CWD

FILENAME = str(CWD / "2fas-demo-pass.2fas")
PASSWORD = "test"


@pytest.fixture()
def clean_keyring():
    # manager classmethods without an instance will clear even active entries.
    KeyringManager.tmp_file.unlink(missing_ok=True)
    KeyringManager._save_credentials("test", "test", "2fas:test")  # dummy insert to test next assert
    assert KeyringManager._cleanup_keyring("")
    assert not KeyringManager._cleanup_keyring("")  # 2nd time should be 0

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


def test_file_missing():
    assert load_services("/tmp/fake_file_for_test_file_missing.2fas", _max_retries=1) is None


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


def test_cleanup():
    KeyringManager._cleanup_keyring("")


def test_dummy_keyring(getpass_correct):
    dummy = DummyKeyringManager()

    key = "test-dummy-keyring"

    assert dummy.retrieve_credentials(key) is None
    assert dummy.save_credentials(key) == PASSWORD
    assert dummy.cleanup_keyring() == -1  # dummy doesn't actually cleanup!
    assert dummy.retrieve_credentials(key) == PASSWORD
    assert dummy.delete_credentials(key) is None
    assert dummy.retrieve_credentials(key) is None
