import datetime

from mappingtools._compat import UTC


def test_utc_is_tzinfo_and_zero_offset():
    # UTC should implement tzinfo and produce zero offset
    now = datetime.datetime.now(tz=UTC)
    assert now.tzinfo is UTC or now.tzinfo is not None
    # offset should be zero
    assert now.utcoffset() == datetime.timedelta(0)
    assert now.tzname() in ("UTC", "UTC")


def test_utc_equivalence_on_py310():
    # On py3.10, mappingtools._compat.UTC should be datetime.timezone.utc
    if hasattr(datetime, "UTC"):
        # If running on Python 3.11+, ensure our UTC is compatible
        assert getattr(datetime, "UTC") == UTC
    else:
        assert datetime.timezone.utc == UTC

