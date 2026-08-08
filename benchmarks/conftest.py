"""Shared datasets for the CodSpeed benchmark suite.

All fixtures are session scoped and deterministic (fixed random seed) so that
successive CodSpeed runs measure the same amount of work.
"""

import random
import string
from dataclasses import dataclass, field

import pytest

SEED = 20240501


@dataclass
class Sensor:
    """A small nested class instance used to exercise class traversal."""

    name: str
    unit: str
    readings: list[float] = field(default_factory=list)


class Greeter:
    """A plain class used to exercise the `structures` proxies."""

    def __init__(self, greeting: str, city: str):
        self.greeting = greeting
        self.city = city

    def greet(self, name: str) -> str:
        return f'{self.greeting}, {name}!'

    @property
    def greeting_length(self) -> int:
        return len(self.greeting)


def _rng() -> random.Random:
    return random.Random(SEED)


def _make_deep_tree(depth: int, value):
    tree = {'leaf': value}
    for level in range(depth):
        tree = {f'child_{level}': tree}
    return tree


def _make_wide_tree(width: int) -> dict:
    return {f'key_{i}': {'value': i, 'leaf': True} for i in range(width)}


@pytest.fixture(scope='session')
def nested_tree() -> dict:
    """A medium sized, mixed dict/list/scalar tree (~250 nodes)."""
    rng = _rng()
    return {
        f'node_{i}': {
            'id': i,
            'config': {
                'param_a': f'value_{i}',
                'param_b': i * 1.1,
                'features': {'f1': True, 'f2': False, 'f3': None},
            },
            'tags': [f'tag_{rng.randint(0, 9)}' for _ in range(5)],
            'samples': [{'x': rng.random(), 'y': rng.random()} for _ in range(3)],
        }
        for i in range(50)
    }


@pytest.fixture(scope='session')
def deep_tree() -> dict:
    return _make_deep_tree(100, 'leaf_value')


@pytest.fixture(scope='session')
def wide_tree() -> dict:
    return _make_wide_tree(1000)


@pytest.fixture(scope='session')
def tree_pair(nested_tree) -> tuple[dict, dict]:
    """Two overlapping trees, suitable for `merge` and `combine`."""
    rng = _rng()
    other = {
        f'node_{i}': {
            'id': i,
            'config': {
                'param_a': f'other_{i}',
                'param_c': i * 2.2,
                'features': {'f2': True, 'f4': True},
            },
            'tags': [f'tag_{rng.randint(0, 9)}' for _ in range(5)],
            'score': rng.random(),
        }
        for i in range(25, 75)
    }
    return nested_tree, other


@pytest.fixture(scope='session')
def records() -> list[dict]:
    """A stream of flat records, suitable for `pivot`, `reshape` and collectors."""
    rng = _rng()
    regions = ('emea', 'apac', 'amer', 'latam')
    products = tuple(f'product_{i}' for i in range(20))
    channels = ('web', 'retail', 'partner')
    return [
        {
            'region': rng.choice(regions),
            'product': rng.choice(products),
            'channel': rng.choice(channels),
            'units': rng.randint(1, 100),
            'amount': round(rng.uniform(1.0, 500.0), 2),
        }
        for _ in range(5000)
    ]


@pytest.fixture(scope='session')
def key_value_pairs() -> list[tuple[str, int]]:
    rng = _rng()
    keys = tuple(f'key_{i}' for i in range(200))
    return [(rng.choice(keys), rng.randint(0, 1000)) for _ in range(10000)]


@pytest.fixture(scope='session')
def words() -> list[str]:
    rng = _rng()
    return [''.join(rng.choices(string.ascii_lowercase, k=rng.randint(3, 10))) for _ in range(5000)]


@pytest.fixture(scope='session')
def mappings() -> list[dict]:
    """Many small mappings sharing keys, suitable for `distinct`."""
    rng = _rng()
    return [{'a': rng.randint(0, 25), 'b': f'v_{rng.randint(0, 25)}', 'c': None} for _ in range(2000)]


@pytest.fixture(scope='session')
def set_mapping() -> dict[str, set]:
    rng = _rng()
    return {f'group_{i}': {f'member_{rng.randint(0, 500)}' for _ in range(20)} for i in range(200)}


@pytest.fixture(scope='session')
def class_tree() -> dict:
    """A tree that mixes mappings, iterables and class instances."""
    rng = _rng()
    return {
        f'station_{i}': {
            'sensors': [
                Sensor(name=f'sensor_{j}', unit='C', readings=[rng.random() for _ in range(5)]) for j in range(4)
            ],
            'meta': {'active': True, 'altitude': i * 3.5, 'labels': (f'l{i}', f'l{i + 1}')},
        }
        for i in range(40)
    }


@pytest.fixture(scope='session')
def document() -> dict:
    """A document with a stable, addressable shape, suitable for optics."""
    return {
        'users': [
            {'name': f'user_{i}', 'profile': {'city': f'city_{i % 7}', 'version': i}, 'roles': ['reader', 'writer']}
            for i in range(100)
        ],
        'meta': {'schema': {'version': 3, 'namespace': 'bench'}, 'checksum': 'abc123'},
    }


@pytest.fixture(scope='session')
def greeters() -> dict[str, Greeter]:
    return {f'greeter_{i}': Greeter(greeting=f'Hello_{i}', city=f'city_{i % 5}') for i in range(200)}


@pytest.fixture(scope='session')
def greeter_type() -> type[Greeter]:
    return Greeter
