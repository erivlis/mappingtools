# Generated by CodiumAI
from mappingtools import nested_defaultdict


class TestNestedDefaultdict:

    #  Creating a nested defaultdict with default depth and factory
    def test_default_depth_and_factory(self):
        from collections import defaultdict
        # Arrange
        result = nested_defaultdict()
        # Act
        value = result['key']
        # Assert
        assert isinstance(result, defaultdict)
        assert value is None

    #  Creating a nested defaultdict with specified depth and default factory
    def test_specified_depth_and_factory(self):
        from collections import defaultdict
        # Arrange
        result = nested_defaultdict(1, int)
        # Act
        value = result['key']['subkey']
        # Assert
        assert isinstance(result, defaultdict)
        assert isinstance(result['key'], defaultdict)
        assert value == 0

    #  Creating a nested defaultdict with additional keyword arguments
    def test_with_additional_kwargs(self):
        from collections import defaultdict
        # Arrange
        result = nested_defaultdict(0, int, key='value')
        # Act
        value = result['key']
        # Assert
        assert isinstance(result, defaultdict)
        assert value == 'value'

    #  Accessing nested levels of the defaultdict to ensure proper nesting
    def test_accessing_nested_levels(self):
        from collections import defaultdict
        # Arrange
        result = nested_defaultdict(2, default_factory=int)
        # Act
        value = result['level1']['level2']['level3']
        # Assert
        assert isinstance(result['level1'], defaultdict)
        assert isinstance(result['level1']['level2'], defaultdict)
        assert value == 0

    #  Using a custom default factory function to initialize values
    def test_custom_default_factory_function(self):
        # Arrange
        def custom_factory():
            return 'custom_value'

        result = nested_defaultdict(0, custom_factory)
        # Act
        value = result['key']
        # Assert
        assert value == 'custom_value'

    #  Specifying a nesting depth of zero
    def test_nesting_depth_zero(self):
        # Arrange
        result = nested_defaultdict(0, default_factory=int)
        # Act
        value = result['key']
        # Assert
        assert value == 0

    #  Providing a non-callable default factory
    def test_non_callable_default_factory(self):
        import pytest
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            nested_defaultdict(1, "not_callable")

    #  Using a negative nesting depth
    def test_negative_nesting_depth(self):
        import pytest
        # Arrange & Act & Assert
        with pytest.raises(ValueError):  # noqa: PT011
            nested_defaultdict(-1, int)

    #  Accessing keys that do not exist in the defaultdict
    def test_accessing_nonexistent_keys(self):
        # Arrange & Act & Assert
        result = nested_defaultdict(1, int)
        assert result['nonexistent']['nonexistent'] == 0  # Default factory returns 0 for int type.

    #  Checking performance with large nesting depths
    def test_large_nesting_depths_performance(self):
        import time

        # Arrange & Act
        start_time = time.time()
        result = nested_defaultdict(100, int)

        # Access deeply nested value to ensure it works correctly.
        current_level = result
        for _ in range(100):
            current_level = current_level['key']

        end_time = time.time()

        # Assert that the operation completes in a reasonable time frame.
        assert (end_time - start_time) < 1  # Should complete within 1 second.

    #  Ensuring immutability of the default factory
    def test_immutability_of_default_factory(self):
        # Arrange
        def custom_factory():
            return []

        result = nested_defaultdict(0, custom_factory)

        # Act
        first_value = result['key']
        first_value.append('item')

        second_value = result['another_key']

        # Assert
        assert first_value == ['item']
        assert second_value == []

    #  Verifying the type of the returned object is defaultdict
    def test_return_type_is_defaultdict(self):
        from collections import defaultdict

        # Arrange & Act
        result = nested_defaultdict(1, int)

        # Assert
        assert isinstance(result, defaultdict)
