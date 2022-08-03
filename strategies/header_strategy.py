from collections import OrderedDict

import regex

from .baseclasses import Strategiser, StrategiserMeta, StrategyException
from .constants import REFERER, USER_AGENT

UNCAPITALISED_MATCHER = regex.compile(r"(?<=^|[-\s]+)([a-z])")


def ordered_headers_strategy(headers: dict):
    return OrderedDict(sorted(headers.copy().items(), key=lambda x: x[0]))


def capitalised_headers_strategy(headers: "dict | OrderedDict"):

    for key in headers:
        replacement = UNCAPITALISED_MATCHER.sub(lambda m: m.group(1).upper(), key)

        if replacement != key:
            headers[replacement] = headers.pop(key)

    return headers


def header_setter(session, headers):
    session.headers = headers


def header_accessor(session):
    return session.headers


def get_header_update_strategy(key, value):
    def strategy(headers):
        if any(header_key.lower() == key.lower() for header_key in headers):
            raise StrategyException(f"{key} header already exists")

        headers[key] = value

    return strategy


class OrderedHeaderStrategy(
    Strategiser,
    metaclass=StrategiserMeta,
    accessor=header_accessor,
    setter=header_setter,
    combinable=True,
    strategy=ordered_headers_strategy,
):
    priority = 0b10
    goal = "Converts the headers to a sorted ordered header list."


class CapitalisedHeaderStrategy(
    Strategiser,
    metaclass=StrategiserMeta,
    accessor=header_accessor,
    setter=header_setter,
    combinable=True,
    strategy=capitalised_headers_strategy,
):
    priority = 0b01
    goal = "Capitalises the headers properly."


def append_header_strategy(
    name: str,
    header_key: str,
    header_value: str,
    goal: str,
):
    return StrategiserMeta(
        name,
        (Strategiser,),
        {
            "__module__": __name__,
            "__qualname__": name,
            "priority": 0b11,
            "goal": goal,
            "header_key": header_key,
            "header_value": header_value,
        },
        accessor=header_accessor,
        setter=None,
        combinable=True,
        strategy=get_header_update_strategy(header_key, header_value),
    )


RefererStrategy = append_header_strategy(
    "RefererStrategy",
    "Referer",
    REFERER,
    goal=f"Sets headers: Referer => {REFERER!r}",
)

XHRStrategy = append_header_strategy(
    "XHRStrategy",
    "X-Requested-With",
    "XMLHttpRequest",
    goal="Sets headers: X-Requested-With => XMLHttpRequest",
)

UserAgentStrategy = append_header_strategy(
    "UserAgentStrategy",
    "User-Agent",
    USER_AGENT,
    goal=f"Sets headers: User-Agent => {USER_AGENT!r}",
)
