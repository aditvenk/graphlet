from __future__ import annotations
from typing import Set, Optional
from .graph import Graph, Node
from .debug import log

class ConstantFolding:
    """Fold add/mul with constant operands; propagate constants.
    Runs to a simple fixed point (single sweep is enough for this toy).
    """
    def run(self, g: Graph) -> Graph:
        g.relink()
        changed = True
        while changed:
            changed = False
            for n in list(g.nodes):
                if n.op in ("add", "mul"):
                    a, b = n.inputs
                    if a.op == "const" and b.op == "const":
                        av = a.attrs["value"]; bv = b.attrs["value"]
                        val = (av + bv) if n.op == "add" else (av * bv)
                        # Replace n with const node
                        c = g.const(val)
                        # Redirect users
                        for u in list(n.users):
                            u.inputs = [c if x is n else x for x in u.inputs]
                        # Remove the old node from graph order (keep order stable: swap in place)
                        idx = g.nodes.index(n)
                        g.nodes[idx] = c
                        changed = True
                        log(f"ConstFold: {n.op}(const({av}), const({bv})) -> const({val})")
            if changed:
                g.relink()
        return g

class DeadCodeElimination:
    """
    Remove nodes that do not contribute to the program outputs.

    This pass performs a backward liveness analysis starting from the graph
    outputs. Nodes that are not reachable from any output are considered dead
    and removed.
    """
    def run(self, g: Graph) -> Graph:
        g.relink()
        live: Set[Node] = set()
        worklist = list(g.outputs)
        while worklist:
            n = worklist.pop()
            if n in live: continue
            live.add(n)
            for i in n.inputs: worklist.append(i)
        g.nodes = [n for n in g.nodes if n in live]
        g.relink()
        return g
