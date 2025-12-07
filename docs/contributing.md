---
icon: lucide/badge-plus
---

# Contributing

## Compatibility

This project exposes `mappingtools._compat.UTC` as a stable UTC tzinfo object that works across Python versions. On
Python 3.11+ it maps to `datetime.UTC`; on earlier versions it maps to `datetime.timezone.utc`.

Use it in your code or tests when you need a timezone-aware UTC datetime:

```python
from mappingtools._compat import UTC
from datetime import datetime

dt = datetime.now(tz=UTC)
```

## Development

### Ruff

```shell
ruff check src

ruff check tests
```

### Test

#### Standard (cobertura) XML Coverage Report

```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=xml
```

#### HTML Coverage Report

```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=html
```
