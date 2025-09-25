from __future__ import annotations
"""
Core graph data structures for Graphlet.

This module defines the Node and Graph classes:
- Node: Represents an operation in the computation graph, with inputs,
  attributes, and users that depend on it.
- Graph: Container for nodes and graph outputs, with helpers for
  creating inputs, constants, and operations, and for relinking or
  dumping the graph for debugging.

These classes form the foundation for compiler passes and execution.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(eq=False)
class Node:
    op: str
    inputs: List["Node"] = field(default_factory=list)
    name: str | None = None
    attrs: Dict[str, Any] = field(default_factory=dict)
    users: set["Node"] = field(default_factory=set, repr=False, compare=False)

    def __repr__(self) -> str:
        if self.op == "input":
            return f"{self.name}" if self.name else "input"
        if self.op == "const":
            return f"const({self.attrs.get('value', None)})"
        args = ", ".join(repr(i) for i in self.inputs)
        return f"{self.op}({args})"

class Graph:
    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.outputs: List[Node] = []

    def input(self, name: str) -> Node:
        n = Node("input", [], name=name); self.nodes.append(n); return n

    def const(self, value: Any) -> Node:
        n = Node("const", [], attrs={"value": value}); self.nodes.append(n); return n

    def add_op(self, op: str, *inputs: Node, **attrs: Any) -> Node:
        n = Node(op, list(inputs), attrs=attrs); self.nodes.append(n); return n

    def set_outputs(self, *nodes: Node) -> None:
        self.outputs = list(nodes)

    def relink(self) -> None:
        for n in self.nodes: n.users.clear()
        for n in self.nodes:
            for i in n.inputs: i.users.add(n)

    def dump(self) -> str:
        lines = []
        for idx, n in enumerate(self.nodes):
            lines.append(f"%{idx}: {n!r}")
        outs = ", ".join(f"%{self.nodes.index(o)}" for o in self.outputs if o in self.nodes)
        lines.append(f"outputs: {outs}")
        return "\n".join(lines)
