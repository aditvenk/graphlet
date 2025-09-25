# graphlet

Graphlet is a tiny, torch-free graph IR, compiler, and bytecode capture playground for building intuition about Python graph capture (inspired by ideas from PyTorch Dynamo).

## What’s inside?

* **Graph IR** – `graphlet.graph` defines lightweight `Graph` and `Node` types with helpers to build inputs, constants, and arithmetic ops.
* **Compiler pipeline** – `graphlet.compiler` runs a configurable pass list. The default pipeline applies constant folding and dead-code elimination from `graphlet.passes`.
* **Runtime** – `graphlet.runtime.execute` eagerly evaluates graphs in pure Python, supporting inputs, constants, `add`, and `mul`, with multi-output support.
* **Bytecode region JIT** – `graphlet.capture.region_jit` interprets a function’s bytecode, captures straight-line `+`/`*` regions into a graph, compiles them, and falls back to Python for anything else.
* **Debug logging** – `graphlet.debug` prints capture/compile activity when `GRAPHLET_DEBUG=1` is set.

## Quick start

Build a graph, compile it, and run it:

```python
from graphlet import Graph, Compiler
from graphlet.runtime import execute

g = Graph()
a = g.input("a")
b = g.input("b")
c = g.add_op("add", a, b)
g.set_outputs(c)

optimized = Compiler().compile(g)
print(execute(optimized, a=2, b=3))  # -> 5
```

## Demos

* **Dead-code elimination:** `python -m examples.demo_dce`
* **Bytecode region JIT:** `python -m examples.demo_region_jit`

The region JIT interpreter walks your function’s bytecode, captures straight-line arithmetic spans (`+`, `*`) into a graph, executes them through the compiler, and falls back to normal Python for unsupported ops such as `**`.

Enable debug tracing to see capture/execution events:

```bash
GRAPHLET_DEBUG=1 python -m examples.demo_region_jit
# [graphlet] CAPTURE op BINARY_MULTIPLY *
# [graphlet] CAPTURE op BINARY_ADD +
# [graphlet] EXEC graph region for node: add(mul(a, b), c)
# [graphlet] FALLBACK Python op ** (power)
```

## Running tests

Graphlet uses `pytest` for testing. Install dev dependencies and run:

```bash
pip install -e ".[dev]"
pytest
```

Target specific tests with familiar `pytest` selectors, e.g.:

```bash
pytest tests/test_dce.py -v
pytest -k "ConstantFolding"
```
