from mappingtools.collectors import AutoMapper


def test_automapper_basic_assignment_and_len_iter_repr():
    # Arrange
    am = AutoMapper(alphabet='AB')

    # Act
    a = am['first']
    b = am['second']
    same_a = am['first']
    items = list(iter(am))
    r = repr(am)
    s = str(am)
    length = len(am)

    # Assert
    assert a == 'A'
    assert b == 'B'
    assert same_a == 'A'
    assert 'first' in items
    assert 'second' in items
    assert 'first' in r
    assert 'second' in r
    assert s == r
    assert length == 2
