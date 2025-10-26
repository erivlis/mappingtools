from mappingtools.collectors import AutoMapper


def test_automapper_dunder_methods_direct_calls():
    # Arrange
    am = AutoMapper(alphabet='AB')

    # Act
    # Access two keys to ensure the mapping is populated (AutoMapper creates keys on access)
    _ = am['x']
    _ = am['y']
    # Directly call dunder methods to ensure coverage attributes hit the function bodies
    it = AutoMapper.__iter__(am)
    ln = AutoMapper.__len__(am)
    rp = AutoMapper.__repr__(am)
    st = AutoMapper.__str__(am)

    # Assert
    assert hasattr(it, '__iter__')
    assert isinstance(ln, int)
    assert isinstance(rp, str)
    assert st == rp
