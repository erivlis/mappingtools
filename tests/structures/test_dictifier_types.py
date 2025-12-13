from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple

from mappingtools.structures import Dictifier


@dataclass
class UserData:
    name: str
    age: int

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"


class SlottedUser:
    __slots__ = ("age", "name")

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"


class TupleUser(NamedTuple):
    name: str
    age: int

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"


# Functional namedtuple
FuncTupleUser = namedtuple("FuncTupleUser", ["name", "age"])


def test_dictifier_dataclass():
    """Test Dictifier with dataclasses."""
    users = Dictifier[UserData]({
        "u1": UserData("Alice", 30),
        "u2": UserData("Bob", 25),
    })

    # Test method access
    greetings = users.greet()
    assert greetings == {
        "u1": "Hi, I'm Alice",
        "u2": "Hi, I'm Bob",
    }

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }


def test_dictifier_slots():
    """Test Dictifier with classes using __slots__."""
    users = Dictifier[SlottedUser]({
        "u1": SlottedUser("Alice", 30),
        "u2": SlottedUser("Bob", 25),
    })

    # Test method access
    greetings = users.greet()
    assert greetings == {
        "u1": "Hi, I'm Alice",
        "u2": "Hi, I'm Bob",
    }

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }


def test_dictifier_named_tuple():
    """Test Dictifier with NamedTuples."""
    users = Dictifier[TupleUser]({
        "u1": TupleUser("Alice", 30),
        "u2": TupleUser("Bob", 25),
    })

    # Test method access
    greetings = users.greet()
    assert greetings == {
        "u1": "Hi, I'm Alice",
        "u2": "Hi, I'm Bob",
    }

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }


def test_dictifier_functional_named_tuple():
    """Test Dictifier with namedtuple created via function."""
    # Note: Functional namedtuples don't easily support custom methods,
    # so we only test field access.
    users = Dictifier[FuncTupleUser]({
        "u1": FuncTupleUser("Alice", 30),
        "u2": FuncTupleUser("Bob", 25),
    })

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }
