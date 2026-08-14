# Player Submission Rules

This is a reference file, not submission code.

Before editing `players/current.py`, read this file and verify the final file against these rules.

## Import Rules

Imports are allow-list based. Only these import roots are allowed:

- `bisect`
- `collections`
- `copy`
- `dataclasses`
- `enum`
- `functools`
- `heapq`
- `itertools`
- `math`
- `operator`
- `othellopy`
- `random`
- `statistics`
- `typing`

All other import roots are forbidden. Examples: `time`, `numpy`, and `pandas` are not allowed.
Relative imports are not allowed.

These imports are explicitly forbidden:

- `asyncio`
- `ctypes`
- `importlib`
- `inspect`
- `marshal`
- `micropip`
- `multiprocessing`
- `os`
- `pathlib`
- `pickle`
- `pyodide`
- `shutil`
- `socket`
- `subprocess`
- `sys`
- `threading`
- `js`

## Top-Level Rules

Only these forms are allowed at file top level:

- comments
- `import ...`
- `from ... import ...`
- `class ...:`
- `def ...:`
- `NAME = ...`
- `NAME: Type = ...`

No top-level executable statements are allowed, such as:

- `if ...`
- `for ...`
- `while ...`
- `try ...`
- `with ...`
- `print(...)`
- `some_function(...)`

Markdown or plain explanation text is not Python code. Use `#` comments for notes inside Python files.

## Forbidden Names

These names must not be used:

- `breakpoint`
- `compile`
- `delattr`
- `eval`
- `exec`
- `getattr`
- `globals`
- `input`
- `locals`
- `open`
- `setattr`
- `vars`

## Forbidden Attributes

These attributes must not be used:

- `__class__`
- `__dict__`
- `__globals__`
- `__mro__`
- `__subclasses__`

## Runtime Rules

- File operations are forbidden.
- Communication/network access is forbidden.
- External process execution is forbidden.
- Long-running or infinite loops fail.
- `next_move` must return a legal move.

