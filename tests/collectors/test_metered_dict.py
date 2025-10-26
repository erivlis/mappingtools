import time
from datetime import UTC, datetime, timedelta

from mappingtools.collectors import DictOperation, MeteredDict


def test_metered_dict_basic_get_set():
    # Arrange
    d = MeteredDict()

    # Act
    d['a'] = 1
    result = d['a']
    set_count = d.count('a', DictOperation.SET)
    get_count = d.count('a', DictOperation.GET)

    # Assert
    assert result == 1
    assert set_count == 1
    assert get_count == 1


def test_metered_dict_get_default():
    # Arrange
    d = MeteredDict()

    # Act
    result = d.get('missing', 42)
    get_default_count = d.count('missing', DictOperation.GET_DEFAULT)

    # Assert
    assert result == 42
    assert get_default_count == 1


def test_metered_dict_setdefault():
    # Arrange
    d = MeteredDict()

    # Act
    d.setdefault('foo', 99)
    result = d['foo']
    set_default_count = d.count('foo', DictOperation.SET_DEFAULT)

    # Assert
    assert result == 99
    assert set_default_count == 1


def test_metered_dict_multiple_accesses():
    # Arrange
    d = MeteredDict()

    # Act
    d['x'] = 10
    d['x'] = 20
    _ = d['x']
    _ = d.get('x')
    set_count = d.count('x', DictOperation.SET)
    get_count = d.count('x', DictOperation.GET)

    # Assert
    assert set_count == 2
    assert get_count == 2


def test_metered_dict_frequency_and_summary():
    # Arrange
    d = MeteredDict()
    operation = DictOperation.SET

    # Act
    d['k'] = 1
    time.sleep(0.01)
    d['k'] = 2
    time.sleep(0.01)
    _ = d['k']
    set_freq = d.frequency('k', operation)
    set_count = d.count('k', operation)
    get_count = d.count('k', DictOperation.GET)
    summary = d.summary()

    # Assert
    assert set_freq.get(operation.repr_name) > 0
    assert operation.repr_name in summary['k']
    assert set_count == 2
    assert get_count == 1
    assert 'k' in summary


def test_metered_dict_used_and_unused_keys():
    # Arrange
    d = MeteredDict()
    d['a'] = 1
    d['b'] = 2

    # Act
    _ = d['a']
    used = d.used_keys(DictOperation.GET)
    unused = d.unused_keys(DictOperation.GET)

    # Assert
    assert 'a' in used
    assert 'b' in unused


def test_metered_dict_used_keys_filters():
    # Arrange
    d = MeteredDict()
    d['a'] = 1
    d['b'] = 2

    # Act
    _ = d['a']
    _ = d['a']
    before = datetime.now(tz=UTC) + timedelta(minutes=1)
    used = d.used_keys(DictOperation.GET, min_count=1, before=before)

    # Assert
    assert 'a' in used
    assert 'b' not in used


def test_metered_dict_reset():
    # Arrange
    d = MeteredDict()
    d['x'] = 10
    _ = d['x']

    # Act
    count_before_reset = d.count('x', DictOperation.GET)
    d.reset()
    count_after_reset = d.count('x', DictOperation.GET)

    # Assert
    assert count_before_reset == 1
    assert count_after_reset == 0


def test_metered_dict_rest_category():
    # Arrange
    d = MeteredDict()
    d['y'] = 20
    _ = d['y']

    # Act
    get_count_before_reset = d.count('y', DictOperation.GET)
    set_count_before_reset = d.count('y', DictOperation.SET)
    d.reset(operations=DictOperation.GET)
    get_count_after_reset = d.count('y', DictOperation.GET)
    set_count_after_reset = d.count('y', DictOperation.SET)

    # Assert
    assert get_count_before_reset == 1
    assert set_count_before_reset == 1
    assert get_count_after_reset == 0
    assert set_count_after_reset == 1


def test_metered_dict_reset_key():
    # Arrange
    d = MeteredDict()
    d['z'] = 30
    _ = d['z']

    # Act
    get_count_before_reset = d.count('z', DictOperation.GET)
    set_count_before_reset = d.count('z', DictOperation.SET)
    d.reset(key='z')
    get_count_after_reset = d.count('z', DictOperation.GET)
    set_count_after_reset = d.count('z', DictOperation.SET)

    # Assert
    assert get_count_before_reset == 1
    assert set_count_before_reset == 1
    assert get_count_after_reset == 0
    assert set_count_after_reset == 0


def test_metered_dict_reset_category_key():
    # Arrange
    d = MeteredDict()
    d['a'] = 30
    d['b'] = 40
    _ = d['a']

    # Act
    get_a_count_before_reset = d.count('a', DictOperation.GET)
    get_b_count_before_reset = d.count('b', DictOperation.GET)
    set_a_count_before_reset = d.count('a', DictOperation.SET)
    set_b_count_before_reset = d.count('b', DictOperation.SET)
    d.reset(operations=DictOperation.GET, key='a')
    get_a_count_after_reset = d.count('a', DictOperation.GET)
    get_b_count_after_reset = d.count('b', DictOperation.GET)
    set_a_count_after_reset = d.count('a', DictOperation.SET)
    set_b_count_after_reset = d.count('b', DictOperation.SET)

    # Assert
    assert get_a_count_before_reset == 1
    assert get_b_count_before_reset == 0
    assert set_a_count_before_reset == 1
    assert set_b_count_before_reset == 1
    assert get_a_count_after_reset == 0
    assert get_b_count_after_reset == 0
    assert set_a_count_after_reset == 1
    assert set_b_count_after_reset == 1
