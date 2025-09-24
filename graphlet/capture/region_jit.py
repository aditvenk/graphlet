from __future__ import annotations
import dis
import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..graph import Graph, Node
from ..compiler import Compiler
from ..runtime import execute
from ..debug import log

SUPPORTED_BIN_OPS = {"BINARY_ADD", "BINARY_MULTIPLY"}
# On 3.11+, many ops are unified under BINARY_OP with argrepr "+", "*"
def is_supported(instr: dis.Instruction) -> bool:
    if instr.opname in SUPPORTED_BIN_OPS:
        return True
    if instr.opname == "BINARY_OP" and instr.argrepr in {"+", "ADD", "*", "MULTIPLY"}:
        return True
    return False

def is_power(instr: dis.Instruction) -> bool:
    return (instr.opname == "BINARY_POWER") or (instr.opname == "BINARY_OP" and instr.argrepr in {"**", "POWER"})

@dataclass
class SymVal:
    """A stack value that is either a symbolic node (captured) or a concrete Python value."""
    node: Optional[Node] = None
    py: Optional[Any] = None

    @property
    def is_sym(self) -> bool: return self.node is not None
    @property
    def is_py(self) -> bool: return self.py is not None

class CaptureSession:
    """Holds a single growing graph and a mapping for input name -> Node."""
    def __init__(self):
        self.g = Graph()
        self.inputs: Dict[str, Node] = {}

    def input(self, name: str) -> Node:
        if name not in self.inputs:
            self.inputs[name] = self.g.input(name)
        return self.inputs[name]

    def const(self, v: Any) -> Node:
        return self.g.const(v)

    def eval_node(self, n: Node, env: Dict[str, Any]) -> Any:
        log(f"EXEC graph region for node: {n}")
        # Temporarily set output to n and execute
        old_outs = list(self.g.outputs)
        self.g.set_outputs(n)
        val = execute(self.g, **env)
        self.g.outputs = old_outs
        return val

class RegionInterpreter:
    """A very small bytecode interpreter that regionizes supported arithmetic (+, *)
    into a captured graph while executing everything else with normal Python semantics.
    """
    def __init__(self, fn):
        self.fn = fn
        self.instructions = list(dis.get_instructions(fn))
        self.session = CaptureSession()
        self.env: Dict[str, Any] = {}   # local variables: name -> concrete Python value or SymVal

    def run(self, *args, **kwargs):
        sig = inspect.signature(self.fn)
        bound = sig.bind_partial(*args, **kwargs); bound.apply_defaults()
        # Initialize locals with *concrete* Python values; we lazily symbolify when needed.
        self.env = dict(bound.arguments)

        stack: List[SymVal] = []

        for instr in self.instructions:
            op = instr.opname

            if op == "RESUME":  # Python 3.11 artifact; ignore
                continue

            if op == "LOAD_FAST":
                v = self.env[instr.argval]
                if isinstance(v, SymVal):
                    stack.append(v)
                else:
                    # push as symbolic input so it can participate in captured regions
                    n = self.session.input(instr.argval)
                    stack.append(SymVal(node=n))
            elif op == "LOAD_CONST":
                stack.append(SymVal(node=self.session.const(instr.argval)))
            elif is_supported(instr):
                log(f"CAPTURE op {instr.opname} {instr.argrepr}")
                # binary op: combine top 2 stack items as symbolic nodes
                b = stack.pop(); a = stack.pop()
                an = a.node if a.is_sym else self.session.const(a.py)
                bn = b.node if b.is_sym else self.session.const(b.py)
                if instr.argrepr in ("*", "MULTIPLY") or op == "BINARY_MULTIPLY":
                    out = self.session.g.add_op("mul", an, bn)
                else:
                    out = self.session.g.add_op("add", an, bn)
                stack.append(SymVal(node=out))
            elif is_power(instr):
                log("FALLBACK Python op ** (power)")
                # Flush: materialize top 2 as Python, compute **, push concrete
                b = stack.pop(); a = stack.pop()
                aval = self._materialize(a)
                bval = self._materialize(b)
                stack.append(SymVal(py=(aval ** bval)))
            elif op == "STORE_FAST":
                v = stack.pop()
                # materialize *only* if concrete Python is required later;
                # we can store symbolic and reuse
                self.env[instr.argval] = v
            elif op == "RETURN_VALUE":
                v = stack.pop()
                return self._materialize(v)
            else:
                # Fallback for any other op: materialize operands as needed
                raise NotImplementedError(f"Unsupported opcode in demo interpreter: {op} ({instr.argrepr})")

        raise RuntimeError("Function ended without RETURN_VALUE")

    def _materialize(self, sv: SymVal) -> Any:
        if sv.is_py:
            return sv.py
        assert sv.is_sym
        # Evaluate symbolic node under current env (materialize any symbolic locals first)
        env_py: Dict[str, Any] = {}
        for name, val in self.env.items():
            if isinstance(val, SymVal):
                env_py[name] = self._materialize(val)
                self.env[name] = SymVal(py=env_py[name])  # cache concrete
            else:
                env_py[name] = val
        return self.session.eval_node(sv.node, env_py)

def region_jit(fn):
    """Decorator: interpret the function's bytecode.
    Supported arithmetic (+, *) is captured as a graph region and executed via the compiler.
    Unsupported ops (e.g., **) are executed with Python semantics, seamlessly interleaving.
    """
    def wrapped(*args, **kwargs):
        return RegionInterpreter(fn).run(*args, **kwargs)
    wrapped.__name__ = f"regionjit_{fn.__name__}"
    return wrapped