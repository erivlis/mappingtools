# AI Tools Protocol

This document defines standard, executable one-liners for AI Agents to verify objective facts (Time, Math) instead of hallucinating them.

## 1. Chronos (Time)
**Goal:** Get a rigorous, ISO-8601 timestamp.
**Command:**
```shell
python -c "import datetime; print(datetime.datetime.now().isoformat())"
```

## 2. Abacus (Simple Arithmetic)
**Goal:** Verify basic arithmetic to avoid token-prediction errors.
**Command:**
```shell
python -c "print({expression})"
```
*Example:* `python -c "print(123 * 456)"`

## 3. Calculator (Advanced Math)
**Goal:** Perform complex calculations (trig, log, exp) using the `math` module.
**Command:**
```shell
python -c "import math; print({expression})"
```
*Example:* `python -c "import math; print(math.sqrt(2) * math.pi)"`

## 4. Randomness (Entropy)
**Goal:** Generate a random seed or UUID.
**Command:**
```shell
python -c "import uuid; print(uuid.uuid4())"
```

## Usage Directive
When an Agent needs to perform a calculation or state the time, it should:
1.  **Not Guess.**
2.  **Propose** the command from this list.
3.  **Wait** for the user to run it (or run it if the environment permits).
