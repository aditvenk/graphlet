# graphlet

A tiny, torch-free graph IR + compiler + bytecode capture to build intuition for Python graph capture (inspired by PyTorch Dynamo).

## Features
- Minimal **IR** (`graphlet.graph`)
- **Compiler** with DCE + constant folding (`graphlet.compiler`, `graphlet.passes`)
- **Executor** to run graphs eagerly (`graphlet.runtime.execute`)
- **Bytecode capture** and **region JIT** (`graphlet.capture`)
- **Debug tracer** to visualize capture and execution (`GRAPHLET_DEBUG=1`)

## Demos

### 1) Dead-Code Elimination
```bash
python -m examples.demo_dce
```

### 2) Capture -> Optimize
```bash
python -m examples.demo_capture
```

### 3) Bytecode region JIT (Dynamo-style partitioning)
```bash
python -m examples.demo_region_jit
```
This interpreter walks your function's bytecode, **captures** straight-line arithmetic spans (`+`, `*`) into a graph,
executes them via the compiler, and **falls back** to Python for unsupported ops (e.g., `**`). The two modes interleave,
so you get partial acceleration without rewriting your code.

### 4) Constant Folding
```bash
python -m examples.demo_constfold
```
This shows how the compiler simplifies constant expressions at compile-time.

## Debug tracer
Set `GRAPHLET_DEBUG=1` to trace region capture and execution:

```bash
GRAPHLET_DEBUG=1 python -m examples.demo_region_jit
# [graphlet] CAPTURE op BINARY_MULTIPLY *
# [graphlet] CAPTURE op BINARY_ADD +
# [graphlet] EXEC graph region for node: add(mul(a, b), c)
# [graphlet] FALLBACK Python op ** (power)
```

## Notes
- `graphlet.capture.frame_eval` is experimental and optional; it is not enabled by default and serves only as an educational scaffold.
