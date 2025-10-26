"""Compatibility helpers for cross-version behavior.

Expose UTC so callers can import a single symbol that works on Python 3.10 and 3.11+.
"""
import datetime as _dt

# Use datetime.UTC when available (Python 3.11+), else fall back to timezone.utc
UTC = getattr(_dt, "UTC", _dt.timezone.utc)

__all__ = ["UTC"]
