"""
This file contains helper functionality.
"""

import typing

from more_itertools import flatten as _flatten
from rapidfuzz import fuzz

T = typing.TypeVar("T")


def flatten(data: list[list[T]]) -> list[T]:
    """
    Flatten a 2D list into a 1D list.
    """
    return list(_flatten(data))


def fuzzy_match(val1: str, val2: str) -> float:
    """
    Wrapper around `fuzz.partial_ratio` with a slighly more friendly name.
    """
    return fuzz.partial_ratio(val1, val2)
