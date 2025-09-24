# graphlet

A tiny, torch-free graph IR + compiler + bytecode capture to build intuition for Python graph capture (inspired by PyTorch Dynamo).

## Features
- Minimal **IR** (`graphlet.graph`)
- **Compiler** with DCE (`graphlet.compiler`, `graphlet.passes`)
- **Executor** to run graphs eagerly (`graphlet.runtime.execute`)
- **Bytecode capture** and **hybrid JIT** (`graphlet.capture`)

## Demos

### 1) Dead-Code Elimination
```bash
python -m examples.demo_dce
```

### 2) Capture -> Optimize
```bash
python -m examples.demo_capture
```

### 3) Hybrid: captured region + Python fallback
```bash
python -m examples.demo_hybrid
```
This runs a captured, optimized sub-function while the rest of the program executes under the normal Python interpreter—mimicking Dynamo-style partitioning.

## Dev
```bash
python -m pip install -U pip
pip install -e ".[dev]"
pytest
```

## Notes
- `graphlet.capture.frame_eval` contains an educational scaffold for the CPython eval-frame hook; it is not used by default.

### 4) Auto-partitioned function (expr-level capture)
```bash
python -m examples.demo_auto_partition
```
This decorates the whole function and **partially captures** any sub-expressions built from `+` and `*`. Everything else (like `**`, loops, I/O) runs in normal Python.


### 5) Bytecode region JIT (Dynamo-style partitioning)
```bash
python -m examples.demo_region_jit
```
This interpreter walks your function's bytecode, **captures** straight-line arithmetic spans (`+`, `*`) into a graph,
executes them via the compiler, and **falls back** to Python for unsupported ops (e.g., `**`). The two modes interleave,
so you get partial acceleration without rewriting your code.


## Debug tracer
Set `GRAPHLET_DEBUG=1` to trace region capture and execution:

```bash
GRAPHLET_DEBUG=1 python -m examples.demo_region_jit
# [graphlet] CAPTURE op BINARY_MULTIPLY *
# [graphlet] CAPTURE op BINARY_ADD +
# [graphlet] EXEC graph region for node: add(mul(a, b), c)
# [graphlet] FALLBACK Python op ** (power)
```
