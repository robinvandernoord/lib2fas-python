import json

import pytest

from src.lib2fas import load_services
from src.lib2fas._types import TwoFactorAuthDetails
from src.lib2fas.core import TwoFactorStorage

from ._shared import CWD

FILENAME = str(CWD / "2fas-demo-nopass.2fas")


def test_empty():
    storage = TwoFactorStorage()
    assert not storage


@pytest.fixture
def services():
    yield load_services(FILENAME)


def test_load(services):
    assert services

    assert len(list(services)) == services.count == 4

    assert len(services.keys()) == 3  # 1 2 and 3

    for name, detail_list in services.items():
        assert isinstance(name, str)
        assert isinstance(detail_list, list)
        assert detail_list  # why would it return an empty list?
        assert isinstance(detail_list[0], TwoFactorAuthDetails)

    service = next(iter(services))
    assert repr(service) == service.as_json() == json.dumps(service.as_dict(), indent=2)

    assert str(service).startswith("<2fas")

    assert "3" in repr(services) and "4" in repr(services)

    example_1 = services["Example 1"]
    example_1a, example_1b = example_1  # type: TwoFactorAuthDetails

    totp_1a = example_1a.generate()
    totp_1b = example_1b.generate_int()

    assert totp_1a
    assert totp_1b

    assert totp_1a != str(totp_1b)
    assert int(totp_1a) != totp_1b

    example_2 = services["Example 2"]
    assert len(example_2) == 1

    example_2 = example_2[0]

    assert str(example_2.generate_int()).rjust(6, "0") == example_2.generate()
    assert example_2.generate_int() == int(example_2.generate())


def test_minimal():
    data = load_services(CWD / "2fas-demo-minimal.2fas")

    entry = data["example 1"][0]

    assert entry
    assert entry.generate() == entry.generate()

    print(repr(entry))


def test_search_exact(services):
    found = services.find("Example 1")
    assert len(found) == 2
    assert list(found) == services["Example 1"]


def test_search_fuzzy(services):
    print(list(services.find()))
    print(services.all())

    assert list(services.find()) == services.all()

    found = services.find("Example")
    assert len(found) == 4

    found = services.find("1")
    assert len(found) == 2

    found = services.find("2")
    assert len(found) == 1

    found = services.find("___")
    assert len(found) == 0

    # search in value

    found = services.find("@google")
    assert len(found) == 2

    found = services.find("Additional inof")  # fuzzy with typo
    assert len(found) == 2

    # test nested search:
    found = services.find("1").find("other")
    assert len(found) == 1

    assert (
        [_[1] for _ in services.generate()]
        == [_[1] for _ in services.find().generate()]
        == [_.generate() for _ in services]
    )  # generate all
