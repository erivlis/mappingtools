from mappingtools.transformers.transformer import Transformer


def test_transformer_circular_detection_and_default_handler():
    # Arrange
    def mapping_handler(obj, t, *args, **kwargs):
        return dict(obj)

    def default_handler(obj):
        return f"def:{obj}"

    transformer = Transformer(mapping_handler=mapping_handler, default_handler=default_handler)

    # Act
    # Transform a mapping
    m = {'a': 1}
    out1 = transformer(m)
    out2 = transformer(m)  # second call should return stored object (not None)

    # Circular: pass same object twice via call chain
    lst = []
    lst.append(lst)
    res = transformer(lst)

    # Assert
    assert out1 == {'a': 1}
    assert out2 == out1
    # For list self-reference, transformer should return something non-None
    # (either stored circular or CIRCULAR_REFERENCE)
    assert res is not None


def test_transformer_returns_none_after_three_calls():
    # Arrange
    def mapping_handler(obj, t, *args, **kwargs):
        # return a transformed mapping (immutable representation)
        return dict(obj)

    t = Transformer(mapping_handler=mapping_handler)
    m = {'a': 1}

    # Act
    first = t(m)
    second = t(m)
    third = t(m)

    # Assert
    assert first == {'a': 1}
    assert second == first
    # third call should return None (objects_counter > 2 path)
    assert third is None
