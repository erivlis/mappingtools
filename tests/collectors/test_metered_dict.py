import time
from datetime import datetime, timedelta

import pytest

from mappingtools._compat import UTC
from mappingtools.collectors import DictOperation, MeteredDict
from mappingtools.collectors.metered_dict import TimeSeries


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
    assert set_count == {'set': 1}
    assert get_count == {'get': 1}


def test_metered_dict_get_default():
    # Arrange
    d = MeteredDict()

    # Act
    result = d.get('missing', 42)
    get_default_count = d.count('missing', DictOperation.GET_DEFAULT)

    # Assert
    assert result == 42
    assert get_default_count == {'get_default': 1}


def test_metered_dict_setdefault():
    # Arrange
    d = MeteredDict()

    # Act
    d.setdefault('foo', 99)
    result = d['foo']
    set_default_count = d.count('foo', DictOperation.SET_DEFAULT)

    # Assert
    assert result == 99
    assert set_default_count == {'set_default': 1}


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
    assert set_count == {'set': 2}
    assert get_count == {'get': 2}


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
    summaries = d.summaries()

    # Assert
    assert set_freq.get(operation.repr_name) > 0
    assert operation.repr_name in summaries['k']
    assert set_count == {operation.repr_name: 2}
    assert get_count == {DictOperation.GET.repr_name: 1}
    assert 'k' in summaries


def test_metered_dict_used_and_unused_keys():
    # Arrange
    d = MeteredDict()
    d['a'] = 1
    d['b'] = 2

    # Act
    _ = d['a']
    used = d.used_keys(operations=DictOperation.GET)
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
    used = d.used_keys(min_count=1, before=before, operations=DictOperation.GET)

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
    assert count_before_reset == {'get': 1}
    assert count_after_reset == {'get': 0}


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
    assert get_count_before_reset == {'get': 1}
    assert set_count_before_reset == {'set': 1}
    assert get_count_after_reset == {'get': 0}
    assert set_count_after_reset == {'set': 1}


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
    assert get_count_before_reset == {'get': 1}
    assert set_count_before_reset == {'set': 1}
    assert get_count_after_reset == {'get': 0}
    assert set_count_after_reset == {'set': 0}


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
    d.reset(key='a', operations=DictOperation.GET)
    get_a_count_after_reset = d.count('a', DictOperation.GET)
    get_b_count_after_reset = d.count('b', DictOperation.GET)
    set_a_count_after_reset = d.count('a', DictOperation.SET)
    set_b_count_after_reset = d.count('b', DictOperation.SET)

    # Assert
    assert get_a_count_before_reset == {'get': 1}
    assert get_b_count_before_reset == {'get': 0}
    assert set_a_count_before_reset == {'set': 1}
    assert set_b_count_before_reset == {'set': 1}
    assert get_a_count_after_reset == {'get': 0}
    assert get_b_count_after_reset == {'get': 0}
    assert set_a_count_after_reset == {'set': 1}
    assert set_b_count_after_reset == {'set': 1}


def test_timeseries_init_invalid_samples_counts():
    # Arrange / Act / Assert
    with pytest.raises(ValueError):
        TimeSeries(samples_counts=1)


def test_timeseries_duration_frequency_and_cma():
    # Arrange
    ts = TimeSeries(samples_counts=3)

    dt1 = datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC)
    dt2 = dt1 + timedelta(seconds=2)
    dt3 = dt2 + timedelta(seconds=3)

    # Act
    ts.add(dt1)
    ts.add(dt2)
    ts.add(dt3)

    # Assert: count and values
    assert ts.count == 3
    assert ts.values() == [dt1, dt2, dt3]

    # Assert: durations and duration() (last - first)
    assert ts.durations() == [timedelta(seconds=2), timedelta(seconds=3)]
    assert ts.duration() == timedelta(seconds=5)

    # Assert: frequency = count / duration_seconds => 3 / 5
    assert ts.frequency() == pytest.approx(3.0 / 5.0)

    # Assert: duration CMA with default weights
    assert ts.duration_cma(None) == pytest.approx(2.5)


def test_timeseries_duration_cma_invalid_weights():
    # Arrange
    ts = TimeSeries(samples_counts=3)
    ts.add(datetime.now(tz=UTC))
    ts.add(datetime.now(tz=UTC) + timedelta(seconds=1))

    # Act / Assert
    with pytest.raises(ValueError):
        ts.duration_cma((1,))


def test_metered_dict_pop_and_popitem_increment_pop_count():
    # Arrange
    d = MeteredDict()
    d['a'] = 1
    d['b'] = 2

    # Act
    popped = d.pop('a')

    # Assert
    assert popped == 1
    assert d.count('a', DictOperation.POP) == {'pop': 1}

    # Act
    key, _val = d.popitem()
    # Assert: popitem should increment pop for the returned key
    assert d.count(key, DictOperation.POP) == {'pop': 1}


def test_atomic_operations_no_valid_raises():
    # Arrange
    d = MeteredDict(operations=DictOperation.GET)

    # Act / Assert
    with pytest.raises(ValueError):
        d._atomic_operations(DictOperation.SET)


def test_setdefault_when_key_exists_returns_default_and_does_not_overwrite():
    # Arrange
    d = MeteredDict()
    d['k'] = 5

    # Act
    res = d.setdefault('k', 99)

    # Assert
    assert res == 99
    assert d['k'] == 5


def test_timeseries_add_none_and_reset_and_empty_duration_frequency_summary():
    # Arrange
    ts = TimeSeries(samples_counts=2)

    # Act / Assert: duration on empty series
    assert ts.duration() == timedelta()
    assert ts.frequency() == pytest.approx(0.0)

    # Act: add with None should use current UTC time
    ts.add()
    assert ts.count == 1
    assert isinstance(ts.first, datetime)
    assert isinstance(ts.last, datetime)

    # Act: reset should clear state
    ts.reset()
    assert ts.count == 0
    assert ts.first is None
    assert ts.last is None

    # Assert: summary of empty series
    s = ts.summary()
    assert s['count'] == 0
    assert s['duration'] == timedelta()
    assert s['frequency'] == pytest.approx(0.0)


def test_duration_cma_returns_zero_when_durations_none():
    # Arrange
    ts = TimeSeries(samples_counts=3)
    ts._durations = None

    # Act / Assert
    assert ts.duration_cma(None) == pytest.approx(0.0)


def test_pop_missing_key_still_records_pop():
    # Arrange
    d = MeteredDict()

    # Act / Assert
    with pytest.raises(KeyError):
        d.pop('missing_key')

    # Assert
    assert d.count('missing_key', DictOperation.POP) == {'pop': 1}


def test_filter_keys_and_counts_and_frequencies_and_unused_keys_with_operations():
    # Arrange
    d = MeteredDict()
    d['a'] = 1
    d['b'] = 2
    # access a once (GET) and set b twice
    _ = d['a']
    d['b'] = 3
    d['b'] = 4

    # Act
    all_counts = d.counts()
    all_freqs = d.frequencies()

    # Assert: counts and frequencies summaries for all keys
    assert 'a' in all_counts
    assert 'b' in all_counts

    assert 'a' in all_freqs
    assert 'b' in all_freqs

    # Arrange predicate: select keys for which operation is GET and count > 0
    def pred(k, o):
        ts = d._metering[o][k]
        return ts.count > 0

    # Act
    filtered = d.filter_keys(pred)

    # Assert
    assert 'a' in filtered
    assert 'b' in filtered

    # Act
    unused_get_default = d.unused_keys(DictOperation.GET_DEFAULT)

    # Assert: unused_keys for GET_DEFAULT should include both keys for GET_DEFAULT
    assert 'a' in unused_get_default
    assert 'b' in unused_get_default


def test_used_keys_strict_inequality_boundaries():
    # Arrange
    d = MeteredDict()
    d['k'] = 1
    # access once
    _ = d['k']

    # Act
    used = d.used_keys(min_count=1, operations=DictOperation.GET)

    # Assert
    assert 'k' not in used

    # Act
    used2 = d.used_keys(min_count=0, operations=DictOperation.GET)

    # Assert
    assert 'k' in used2


def test_counts_and_frequencies_explicit():
    # Arrange
    d = MeteredDict()
    d['a'] = 1
    d['b'] = 2
    # perform some operations
    _ = d['a']
    d['b'] = 3

    # Act
    counts = d.counts()
    freqs = d.frequencies()

    # Assert: counts and frequencies summaries for all keys
    assert isinstance(counts, dict)
    assert 'a' in counts
    assert 'b' in counts
    # counts should contain dicts with string keys
    assert all(isinstance(v, dict) for v in counts.values())

    assert isinstance(freqs, dict)
    assert 'a' in freqs
    assert 'b' in freqs
    assert all(isinstance(v, dict) for v in freqs.values())


def test_duration_cma_with_samples2_and_durations_none():
    # Arrange
    ts = TimeSeries(samples_counts=2)
    ts._durations = None

    # Act / Assert
    assert ts.duration_cma(None) == pytest.approx(0.0)


def test__add_no_metering_for_operation_is_noop():
    # Arrange
    d = MeteredDict(operations=DictOperation.GET)

    # Act
    d._add('somekey', DictOperation.SET)

    # Assert
    with pytest.raises(ValueError):
        d.count('somekey', DictOperation.SET)
