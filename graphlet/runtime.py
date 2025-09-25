from __future__ import annotations
"""
Simplistic runtime for executing Graphlet graphs.

This runtime is intended primarily for demonstration and testing.
It provides eager evaluation of graphs using pure Python semantics
and a small set of supported operations (currently input, const,
add, and mul).

The execution is recursive: each node is evaluated on demand,
and results are memoized in a cache to avoid recomputation.
This design is not optimized for performance, but offers clarity
and simplicity for understanding how graphs are executed.
"""
from typing import Any, Dict
from .graph import Graph, Node

def _eval_node(n: Node, env: Dict[str, Any], cache: Dict[Node, Any]) -> Any:
    if n in cache: return cache[n]
    if n.op == "input":
        val = env[n.name]
    elif n.op == "const":
        val = n.attrs["value"]
    elif n.op == "add":
        a = _eval_node(n.inputs[0], env, cache)
        b = _eval_node(n.inputs[1], env, cache)
        val = a + b
    elif n.op == "mul":
        a = _eval_node(n.inputs[0], env, cache)
        b = _eval_node(n.inputs[1], env, cache)
        val = a * b
    else:
        raise NotImplementedError(f"Execution not supported for op: {n.op}")
    cache[n] = val
    return val

def execute(g: Graph, **inputs) -> Any:
    """Eagerly execute a single-output graph with Python semantics."""
    cache: Dict[Node, Any] = {}
    if len(g.outputs) != 1:
        raise ValueError("execute() expects exactly one output")
    return _eval_node(g.outputs[0], inputs, cache)
