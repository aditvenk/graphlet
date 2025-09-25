from __future__ import annotations
"""
Simplistic runtime for executing Graphlet graphs.

This runtime is intended primarily for demonstration and testing.
It provides eager evaluation of graphs using pure Python semantics
and a small set of supported operations (currently input, const,
add, and mul). It supports one or more outputs: a single output returns a bare value; multiple outputs return a tuple in the order specified by the graph.

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
    """Eagerly execute a graph with Python semantics.

    Returns:
        - Bare value if the graph has exactly one output.
        - Tuple of values if the graph has 2 or more outputs (in the order of g.outputs).
    """
    cache: Dict[Node, Any] = {}
    if not g.outputs:
        raise ValueError("execute() expects at least one output")
    if len(g.outputs) == 1:
        return _eval_node(g.outputs[0], inputs, cache)
    return tuple(_eval_node(o, inputs, cache) for o in g.outputs)
