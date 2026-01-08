import pytest

from mappingtools.algebra.semiring import StandardSemiring, TropicalSemiring
from mappingtools.algebra.trie import AlgebraicTrie


def test_algebraic_trie_basic_operations():
    trie = AlgebraicTrie(StandardSemiring)

    # Test __setitem__ and __getitem__
    trie[('a', 'b')] = 1.0
    assert trie[('a', 'b')] == 1.0

    with pytest.raises(KeyError):
        _ = trie[('a', 'c')]

    # Test __len__
    trie[('a', 'c')] = 2.0
    assert len(trie) == 2

    # Test __iter__
    keys = set(trie)
    assert keys == {('a', 'b'), ('a', 'c')}

    # Test __delitem__
    del trie[('a', 'b')]
    assert len(trie) == 1
    with pytest.raises(KeyError):
        _ = trie[('a', 'b')]


def test_algebraic_addition():
    trie = AlgebraicTrie(StandardSemiring)

    # Standard Semiring: + is addition
    trie.add(('x',), 10)
    trie.add(('x',), 5)

    assert trie[('x',)] == 15


def test_tropical_trie():
    # Tropical: + is min, * is +
    trie = AlgebraicTrie(TropicalSemiring)

    trie.add(('path',), 10)
    trie.add(('path',), 5)  # min(10, 5) = 5
    trie.add(('path',), 20)  # min(5, 20) = 5

    assert trie[('path',)] == 5


def test_contraction():
    trie = AlgebraicTrie(StandardSemiring)

    # Setup:
    # root -> a -> 1
    # root -> a -> b -> 2
    # root -> b -> 5

    trie[('a',)] = 1
    trie[('a', 'b')] = 2
    trie[('b',)] = 5

    # Contract everything (prefix=())
    # Sum = 1 + 2 + 5 = 8
    assert trie.contract() == 8

    # Contract under 'a'
    # Sum = 1 (at 'a') + 2 (at 'a/b') = 3
    assert trie.contract(('a',)) == 3

    # Contract under 'b'
    assert trie.contract(('b',)) == 5

    # Contract under unknown
    assert trie.contract(('z',)) == 0  # Zero of StandardSemiring


def test_string_keys():
    # The Generic[K] allows strings as keys if treated as iterable,
    # but usually we pass the iterable of keys.
    # If K is str, then key is tuple[str, ...].

    trie = AlgebraicTrie[str, int](StandardSemiring)
    trie.add(['home', 'user'], 1)
    trie.add(['home', 'bin'], 1)

    assert trie.contract(['home']) == 2
