"""
This file holds reusable types.
"""

import typing
from typing import Optional

from configuraptor import TypedConfig, asdict, asjson
from pyotp import TOTP

AnyDict = dict[str, typing.Any]


class OtpDetails(TypedConfig):
    """
    Fields under the 'otp' key of the 2fas file.
    """

    link: Optional[str] = None
    tokenType: Optional[str] = None
    source: Optional[str] = None
    label: Optional[str] = None
    account: Optional[str] = None
    digits: Optional[int] = None
    period: Optional[int] = None


class OrderDetails(TypedConfig):
    """
    Fields under the 'order' key of the 2fas file.
    """

    position: int = 0


class IconCollectionDetails(TypedConfig):
    """
    Fields under the 'icon.iconCollection' key of the 2fas file.
    """

    id: str


class IconDetails(TypedConfig):
    """
    Fields under the 'icon' key of the 2fas file.
    """

    selected: str
    iconCollection: IconCollectionDetails


class TwoFactorAuthDetails(TypedConfig):
    """
    Fields of a service in a 2fas file.
    """

    name: str
    secret: str
    updatedAt: int
    serviceTypeID: Optional[str]
    otp: Optional[OtpDetails] = None
    order: Optional[OrderDetails] = None
    icon: Optional[IconDetails] = None
    groupId: Optional[str] = None  # todo: groups are currently not supported!

    _topt: Optional[TOTP] = None  # lazily loaded when calling .totp or .generate()

    @property
    def totp(self) -> TOTP:
        """
        Get a TOTP instance for this service.
        """
        if not self._topt:
            self._topt = TOTP(self.secret)
        return self._topt

    def generate(self) -> str:
        """
        Generate the current TOTP code.
        """
        return self.totp.now()

    def generate_int(self) -> int:
        """
        Generate the current TOTP code, as a number instead of string.

        !!! usually not prefered, because this drops leading zeroes!!
        """
        return int(self.totp.now())

    def as_dict(self) -> AnyDict:
        """
        Dump this object as a dictionary.
        """
        return asdict(self, with_top_level_key=False, exclude_internals=2)

    def as_json(self) -> str:
        """
        Dump this object as a JSON string.
        """
        return asjson(self, with_top_level_key=False, indent=2, exclude_internals=2)

    def __str__(self) -> str:
        """
        Magic method for str() - simple representation.
        """
        return f"<2fas '{self.name}'>"

    def __repr__(self) -> str:
        """
        Magic method for repr() - representation in JSON.
        """
        return self.as_json()


T_TypedConfig = typing.TypeVar("T_TypedConfig", bound=TypedConfig)


def into_class(entries: list[AnyDict], klass: typing.Type[T_TypedConfig]) -> list[T_TypedConfig]:
    """
    Helper to load a list of dicts into a list of Typed Config instances.
    """
    return [klass.load(d) for d in entries]
